// Border Manager - handles local border storage and updates
class BorderManager {
  constructor() {
    this.borders = null;
    this.map = null;
    this.source = null;
  }

  async initialize(map) {
    console.log("BorderManager initialize called");
    this.map = map;
    this.source = map.getSource("borders");
    
    // Load initial borders from static file
    try {
      console.log("Loading borders-enhanced-detailed.json");
      const response = await fetch('/borders-enhanced-detailed.json?v=' + Date.now());
      this.borders = await response.json();
      this.source.setData(this.borders);
      console.log(`Loaded ${this.borders.features.length} countries with enhanced political data and detailed borders`);
      
      // Debug faction distribution
      const factions = {};
      this.borders.features.forEach(f => {
        const faction = f.properties.faction;
        factions[faction] = (factions[faction] || 0) + 1;
      });
      console.log('Faction distribution:', factions);
      
      // Debug NATO_ALIGNED countries
      const natoAligned = this.borders.features.filter(f => f.properties.faction === 'NATO_ALIGNED');
      console.log('NATO_ALIGNED countries:', natoAligned.map(f => f.properties.name));
      

      
      // Check for nuclear weapons in the data
      const nuclearCountries = this.borders.features.filter(f => f.properties.nuclear_weapons > 0);
      console.log(`Found ${nuclearCountries.length} countries with nuclear weapons:`, 
        nuclearCountries.map(f => `${f.properties.name} (${f.properties.nuclear_weapons})`));
      
      // Update nuclear indicators after borders load
      console.log("Calling updateNuclearIndicators");
      this.updateNuclearIndicators();
    } catch (error) {
      console.error('Failed to load enhanced detailed borders:', error);
      // Fallback to original borders
      try {
        const fallbackResponse = await fetch('/borders.json?v=' + Date.now());
        this.borders = await fallbackResponse.json();
        this.source.setData(this.borders);
        console.log(`Loaded ${this.borders.features.length} countries with fallback data`);
      } catch (fallbackError) {
        console.error('Failed to load fallback borders:', fallbackError);
      }
    }
  }

  updateNuclearIndicators() {
    console.log("=== updateNuclearIndicators called ===");
    if (!this.map || !this.borders) {
      console.log("❌ Missing map or borders data");
      console.log("Map:", !!this.map);
      console.log("Borders:", !!this.borders);
      return;
    }
    
    const nuclearData = {
      type: "FeatureCollection",
      features: []
    };
    
    console.log(`🔍 Checking ${this.borders.features.length} countries for nuclear weapons`);
    
    // Extract nuclear countries and calculate their centers
    let foundNuclear = 0;
    this.borders.features.forEach((feature, index) => {
      const props = feature.properties;
      
      // Debug first few countries
      if (index < 5) {
        console.log(`Country ${index}: ${props.name} - nuclear_weapons: ${props.nuclear_weapons}, status: ${props.nuclear_status}`);
      }
      
      if ((props.nuclear_weapons > 0 && props.nuclear_status !== 'none') || 
          (props.nuclear_status === 'suspected')) {
        foundNuclear++;
        console.log(`✅ Processing nuclear country: ${props.name} with ${props.nuclear_weapons} warheads`);
        
        // Use capital coordinates if available, otherwise calculate geometric center
        let centerLng, centerLat;
        
        if (props.capital && Array.isArray(props.capital) && props.capital.length === 2) {
          // Use capital coordinates
          centerLng = props.capital[0];
          centerLat = props.capital[1];
          console.log(`📍 Capital: [${centerLng}, ${centerLat}]`);
        } else {
          // Fallback to geometric center calculation
          centerLng = 0;
          centerLat = 0;
          let totalPoints = 0;
          
          if (feature.geometry.type === 'Polygon') {
            const coords = feature.geometry.coordinates[0]; // First ring
            coords.forEach(coord => {
              centerLng += coord[0];
              centerLat += coord[1];
              totalPoints++;
            });
          } else if (feature.geometry.type === 'MultiPolygon') {
            feature.geometry.coordinates.forEach(polygon => {
              polygon[0].forEach(coord => {
                centerLng += coord[0];
                centerLat += coord[1];
                totalPoints++;
              });
            });
          }
          
                     if (totalPoints > 0) {
             centerLng /= totalPoints;
             centerLat /= totalPoints;
             console.log(`📍 Geometric center: [${centerLng}, ${centerLat}]`);
           } else {
             console.log(`❌ No valid coordinates for ${props.name}`);
             return; // Skip this iteration
           }
        }
        
        nuclearData.features.push({
          type: "Feature",
          id: props.id || `nuclear-${props.name}`,
          properties: props,
          geometry: {
            type: "Point",
            coordinates: [centerLng, centerLat]
          }
        });
      }
    });
    
    console.log(`🎯 Created ${nuclearData.features.length} nuclear indicators (found ${foundNuclear} nuclear countries)`);
    console.log("📊 Nuclear data:", nuclearData);
    
    // Update nuclear indicators source
    const nuclearSource = this.map.getSource("nuclear-indicators");
    if (nuclearSource) {
      console.log("🔄 Updating nuclear indicators source");
      nuclearSource.setData(nuclearData);
      console.log("✅ Nuclear indicators source updated successfully");
    } else {
      console.error("❌ Nuclear indicators source not found!");
      console.log("Available sources:", this.map.getStyle().sources);
    }
  }

  // Apply a border update from the backend
  applyUpdate(countryId, updates) {
    if (!this.borders || !this.source) return;

    const feature = this.borders.features.find(f => f.properties.id === countryId);
    if (!feature) {
      console.warn(`Country ${countryId} not found in local borders`);
      return;
    }

    // Apply updates to local data
    if (updates.faction !== undefined) {
      feature.properties.faction = updates.faction;
    }
    if (updates.morale !== undefined) {
      feature.properties.morale = updates.morale;
    }
    if (updates.geometry !== undefined) {
      feature.geometry = updates.geometry;
    }

    // Update the map source
    this.source.setData(this.borders);
    console.log(`Updated ${countryId}:`, updates);
    
    // Update nuclear indicators if this affects nuclear data
    if (updates.nuclear_weapons !== undefined || updates.nuclear_status !== undefined) {
      this.updateNuclearIndicators();
    }
  }

  // Get current border data
  getBorders() {
    return this.borders;
  }

  // Get a specific country
  getCountry(countryId) {
    if (!this.borders) return null;
    return this.borders.features.find(f => f.properties.id === countryId);
  }

  // Update local borders (for testing)
  updateLocalBorders(newBorders) {
    this.borders = newBorders;
    if (this.source) {
      this.source.setData(this.borders);
    }
  }
}

export default BorderManager; 