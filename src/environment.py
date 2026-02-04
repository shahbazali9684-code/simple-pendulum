import random
import math

class DailyWeather:
    def __init__(self, t_min, t_max, humidity, solar_rad, precip, leaf_wetness_hours=0):
        self.t_min = t_min
        self.t_max = t_max
        self.humidity = humidity
        self.solar_rad = solar_rad # 0.0 to 1.0 relative intensity
        self.precip = precip # inches
        self.leaf_wetness_hours = leaf_wetness_hours

    def __repr__(self):
        return f"T_min: {self.t_min:.1f}F, T_max: {self.t_max:.1f}F, Hum: {self.humidity:.1f}%, Rain: {self.precip:.2f}in"

class Environment:
    def __init__(self):
        # Simulation starts in late winter/early spring. Day 60 ~ March 1st.
        self.day_of_year = 60

        # Soil State
        self.soil_moisture = 0.8  # 0.0 (bone dry) to 1.0 (saturation)
        self.soil_ph = 6.5 # Default slightly acidic

        # Location State
        self.is_indoors = True

        # Indoor Controls
        self.indoor_temp_target = 75.0
        self.indoor_light_intensity = 0.8
        self.indoor_humidity = 50.0

    def set_indoors(self, is_indoors: bool):
        self.is_indoors = is_indoors

    def set_indoor_controls(self, temp=None, light=None):
        if temp is not None:
            self.indoor_temp_target = temp
        if light is not None:
            self.indoor_light_intensity = light

    def generate_daily_weather(self):
        # 1. Generate Outdoor Weather
        # Seasonal curve
        # Peak at day 200 (mid-July), trough at day 20 (Jan)
        # Base avg ~50F in spring, ~85F in summer

        # Normalized season (-1 to 1)
        season_offset = -math.cos((self.day_of_year - 20) * 2 * math.pi / 365)

        avg_seasonal_temp = 55 + 30 * season_offset # 25F to 85F range approx

        # Random daily fluctuation (weather fronts)
        daily_fluct = random.uniform(-10, 10)
        day_avg = avg_seasonal_temp + daily_fluct

        # Diurnal range
        diurnal_range = random.uniform(15, 25)
        t_max = day_avg + (diurnal_range / 2)
        t_min = day_avg - (diurnal_range / 2)

        # Precipitation & Humidity
        is_rainy = random.random() < 0.25 # 25% chance of rain

        if is_rainy:
            precip = random.uniform(0.1, 1.5)
            humidity = random.uniform(70, 100)
            solar_rad = random.uniform(0.2, 0.5)
            leaf_wetness_hours = random.uniform(4, 24)
        else:
            precip = 0.0
            humidity = random.uniform(30, 70)
            solar_rad = random.uniform(0.6, 1.0)
            leaf_wetness_hours = 0 if humidity < 60 else random.uniform(0, 4)

        outdoor_weather = DailyWeather(t_min, t_max, humidity, solar_rad, precip, leaf_wetness_hours)

        # Advance day
        self.day_of_year += 1

        # Return effective weather for the plant
        if self.is_indoors:
            # Indoor environment is controlled but maybe affected by outdoor if greenhouse?
            # Assuming home setup: completely controlled.
            return DailyWeather(
                t_min=self.indoor_temp_target - 2,
                t_max=self.indoor_temp_target + 2,
                humidity=self.indoor_humidity,
                solar_rad=self.indoor_light_intensity,
                precip=0,
                leaf_wetness_hours=0 # Usually dry indoors unless misted
            )
        else:
            return outdoor_weather

    def update_soil_moisture(self, weather: DailyWeather, irrigation_amount: float, plant_usage: float, drainage_factor=0.1):
        """
        Updates soil moisture based on inputs and outputs.
        irrigation_amount: inches (approx) applied
        plant_usage: relative 0-1 scale of consumption
        """
        # 1 inch of water fills soil capacity? Simplified model:
        # Assume 1.0 capacity represents "Field Capacity".
        # 1 inch of rain might add 0.3 to the 0-1 scale depending on soil depth/type.
        # Let's say 1 unit of moisture = 3 inches of water storage in root zone.

        inflow = (irrigation_amount + (weather.precip if not self.is_indoors else 0)) / 3.0

        # Evaporation
        # Driven by T_max and Solar Rad
        evap_base = (weather.t_max / 100.0) * weather.solar_rad * 0.05

        # Plant Transpiration
        transpiration = plant_usage * 0.1 # Max daily usage

        total_loss = evap_base + transpiration

        self.soil_moisture += inflow
        self.soil_moisture -= total_loss

        # Drainage / Saturation
        if self.soil_moisture > 1.0:
            # Excess drains away
            self.soil_moisture = 1.0

        if self.soil_moisture < 0.0:
            self.soil_moisture = 0.0

    def get_status(self):
        loc = "Indoors" if self.is_indoors else "Outdoors"
        return f"Location: {loc} | Soil Moisture: {self.soil_moisture*100:.0f}%"
