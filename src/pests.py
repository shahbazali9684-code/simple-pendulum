import random
from src.environment import DailyWeather
from src.plant import Plant

class PestManager:
    def __init__(self):
        self.active_diseases = set()

    def check_daily(self, plant: Plant, weather: DailyWeather, soil_moisture: float):
        events = []

        # 1. Damping Off (Seedling Stage)
        # Risk: High soil moisture + cool temps (or just very wet)
        if plant.bbch_stage < 20 and plant.bbch_stage > 0:
            # If soil is saturated
            if soil_moisture > 0.9:
                risk_prob = 0.05 # 5% daily chance if saturated
                if random.random() < risk_prob:
                    events.append("Damping Off: Seedling wilting at soil line.")
                    plant.health -= 0.3

        # 2. Early Blight (Vegetative -> Fruiting)
        # Risk: Leaf wetness + warm days
        if plant.bbch_stage > 20:
            # Inoculum accumulates
            if weather.leaf_wetness_hours > 8 and weather.t_avg() > 60:
                risk_prob = 0.05
                if random.random() < risk_prob:
                    if "Early Blight" not in self.active_diseases:
                        self.active_diseases.add("Early Blight")
                        events.append("Early Blight: Characteristic target-spots on leaves.")
                    else:
                        # Existing infection worsens
                        plant.health -= 0.02

        if "Early Blight" in self.active_diseases:
            # Chronic damage
            plant.leaf_area *= 0.99
            plant.health -= 0.005

        # 3. Blossom End Rot (Fruiting)
        # Risk: Inconsistent moisture (calcium deficiency proxy)
        if 70 <= plant.bbch_stage <= 85:
            if soil_moisture < 0.3 or soil_moisture > 0.9:
                risk_prob = 0.1
                if random.random() < risk_prob:
                    events.append("Blossom End Rot: Dark spots on fruit bottoms.")
                    plant.fruit_biomass *= 0.95 # Loss of yield

        # 4. Late Blight (The "Fast Collapse")
        # Risk: Cool, wet, humid
        if plant.bbch_stage > 40:
             if weather.humidity > 90 and weather.t_avg() < 75:
                 risk_prob = 0.02 # Low probability event but high impact
                 if random.random() < risk_prob:
                     events.append("LATE BLIGHT OUTBREAK: Rapid tissue collapse!")
                     plant.health -= 0.4
                     plant.leaf_area *= 0.5

        return events

# Helper for t_avg which isn't on DailyWeather directly but computable
def get_t_avg(w: DailyWeather):
    return (w.t_min + w.t_max) / 2
DailyWeather.t_avg = get_t_avg
