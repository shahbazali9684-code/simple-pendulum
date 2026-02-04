SPECIES_DATA = {
    "Tomato": {
        "base_temp": 50.0,
        "opt_temp": 77.0,
        "stage_thresholds": {
            9: 100,   # Emergence
            19: 500,  # Leaf Development (Transplant ready around here)
            51: 800,  # Flower Buds
            60: 1000, # Flowering
            71: 1200, # Fruit Set
            81: 1800, # Ripening
            89: 2200  # Harvest End
        },
        "max_leaf_area": 5000,
        "description": "Annual fruiting crop, sensitive to frost."
    },
    # Future placeholder for Perennials
    "Apple": {
        "base_temp": 40.0,
        "opt_temp": 70.0,
        "stage_thresholds": {
            # Multi-year logic would need separate handling for "Age"
            7: 50, # Bud break
            60: 300, # Bloom
            71: 500, # Fruit Set
            87: 2500 # Harvest
        },
        "max_leaf_area": 50000,
        "description": "Woody perennial, requires chill hours."
    }
}
