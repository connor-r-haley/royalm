// Border Manager - handles local border storage and updates
class BorderManager {
  constructor() {
    this.borders = null;
    this.map = null;
    this.source = null;
  }

  async initialize(map) {
    this.map = map;
    this.source = map.getSource("borders");
    
    // Load initial borders from static file
    try {
      const response = await fetch('/borders-enhanced-detailed.json?v=' + Date.now());
      this.borders = await response.json();
      this.source.setData(this.borders);
      
      this.updateNuclearIndicators();
    } catch (error) {
      console.error('Failed to load enhanced detailed borders:', error);
      // Fallback to original borders
      try {
        const fallbackResponse = await fetch('/borders.json?v=' + Date.now());
        this.borders = await fallbackResponse.json();
        this.source.setData(this.borders);
      } catch (fallbackError) {
        console.error('Failed to load fallback borders:', fallbackError);
      }
    }
  }

  updateNuclearIndicators() {
    if (!this.map || !this.borders) {
      return;
    }
    
    const nuclearData = {
      type: "FeatureCollection",
      features: []
    };
    
    // Extract nuclear countries and calculate their centers
    this.borders.features.forEach((feature) => {
      const props = feature.properties;
      
      if ((props.nuclear_weapons > 0 && props.nuclear_status !== 'none') || 
          (props.nuclear_status === 'suspected')) {
        
        // Use capital coordinates if available, otherwise calculate geometric center
        let centerLng, centerLat;
        
        if (props.capital && Array.isArray(props.capital) && props.capital.length === 2) {
          // Use capital coordinates
          centerLng = props.capital[0];
          centerLat = props.capital[1];
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
          } else {
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
    
    // Update nuclear indicators source
    const nuclearSource = this.map.getSource("nuclear-indicators");
    if (nuclearSource) {
      nuclearSource.setData(nuclearData);
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