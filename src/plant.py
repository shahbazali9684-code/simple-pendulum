from src.environment import DailyWeather
from src.config import SPECIES_DATA

class Plant:
    def __init__(self, species_name="Tomato"):
        self.species_name = species_name

        # Load Config
        config = SPECIES_DATA.get(species_name, SPECIES_DATA["Tomato"])
        self.base_temp = config["base_temp"]
        self.opt_temp = config["opt_temp"]
        self.stage_thresholds = config["stage_thresholds"]
        self.max_leaf_area = config.get("max_leaf_area", 5000)

        self.bbch_stage = 0
        self.gdd_accumulated = 0.0

        # Physiological State
        self.leaf_area = 0.0 # cm2 approx
        self.root_capacity = 0.0 # Relative 0-1
        self.biomass = 0.0
        self.height = 0.0

        # Reproductive State
        self.is_flowering = False
        self.flower_count = 0
        self.fruit_set_count = 0
        self.fruit_biomass = 0.0
        self.ripe_fruit_count = 0

        # Stress Trackers
        self.water_stress_days = 0
        self.nutrient_stress = 0.0
        self.health = 1.0 # 0.0 (dead) to 1.0 (perfect)

    def update_daily(self, weather: DailyWeather, soil_moisture: float):
        if self.health <= 0:
            return # Dead plants don't grow

        # 1. Thermal Time Calculation (GDD)
        avg_temp = (weather.t_min + weather.t_max) / 2
        daily_gdd = max(0, avg_temp - self.base_temp)

        # Cap GDD if temp is too high (heat stress slows development)
        heat_stress_threshold = self.opt_temp + 15
        if avg_temp > heat_stress_threshold:
            daily_gdd = max(0, daily_gdd - (avg_temp - heat_stress_threshold))

        self.gdd_accumulated += daily_gdd

        # 2. Update Stage
        self._update_stage()

        # 3. Water Stress Calculation
        # Optimal moisture is 0.4 to 0.8
        stress_factor = 0.0
        if soil_moisture < 0.3:
            stress_factor = (0.3 - soil_moisture) / 0.3 # Rising stress as dry
        elif soil_moisture > 0.95:
            stress_factor = (soil_moisture - 0.95) / 0.05 # Waterlogging

        if stress_factor > 0:
            self.water_stress_days += 1
            self.health -= (stress_factor * 0.01) # Slow health decay
        else:
            self.health = min(1.0, self.health + 0.005) # Recovery

        # 4. Growth Calculation (simplified)
        # Driven by GDD + Light + Water + Health
        growth_potential = daily_gdd * weather.solar_rad * (1.0 - stress_factor) * self.health

        if self.bbch_stage < 10:
            # Germinating - needs warmth/moisture, no light growth yet
            pass
        elif self.bbch_stage < 50:
            # Vegetative
            self.leaf_area += growth_potential * 0.5
            self.root_capacity += growth_potential * 0.2
            self.height += growth_potential * 0.1
        elif self.bbch_stage >= 60:
            # Reproductive - shift allocation
            if self.bbch_stage < 70:
                # Flowering
                self.flower_count += int(growth_potential * 0.1)
            else:
                # Fruiting
                self.fruit_biomass += growth_potential * 0.8
                # Ripening
                if self.bbch_stage >= 81:
                    # Conversion to ripe
                    new_ripe = int(growth_potential * 0.05)
                    if self.fruit_set_count > 0:
                        self.ripe_fruit_count += new_ripe
                        self.fruit_set_count -= new_ripe # Move from green to ripe bucket (simplified)

    def _update_stage(self):
        # Determine current stage based on GDD
        # This is a one-way latch
        current_stage = self.bbch_stage

        for stage_code, threshold in sorted(self.stage_thresholds.items()):
            if self.gdd_accumulated >= threshold:
                if stage_code > current_stage:
                    self.bbch_stage = stage_code

    def get_water_consumption(self):
        # Return 0-1 scale relative to full canopy
        if self.bbch_stage < 10:
            return 0.05

        # Sigmoid function of leaf area approx
        usage = min(1.0, self.leaf_area / (self.max_leaf_area * 0.5))
        return usage

    def get_narrative_status(self):
        # Return a string description of the plant
        stage_desc = "Dormant/Seed"
        if self.bbch_stage >= 9: stage_desc = "Germinated/Emerging"
        if self.bbch_stage >= 10: stage_desc = "Seedling/Vegetative"
        if self.bbch_stage >= 51: stage_desc = "Buds Forming"
        if self.bbch_stage >= 60: stage_desc = "Flowering"
        if self.bbch_stage >= 71: stage_desc = "Fruit Developing"
        if self.bbch_stage >= 81: stage_desc = "Ripening"

        return f"Stage: {self.bbch_stage} ({stage_desc}) | Health: {self.health*100:.0f}% | Height: {self.height:.1f}cm"
