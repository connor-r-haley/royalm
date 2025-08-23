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
      const response = await fetch('/borders.json');
      this.borders = await response.json();
      this.source.setData(this.borders);
      console.log(`Loaded ${this.borders.features.length} countries with real borders`);
    } catch (error) {
      console.error('Failed to load borders:', error);
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