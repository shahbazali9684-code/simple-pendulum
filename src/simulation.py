from src.environment import Environment
from src.plant import Plant
from src.pests import PestManager

class SimulationEngine:
    def __init__(self):
        self.plant = Plant()
        self.environment = Environment()
        self.pests = PestManager()
        self.week = 0
        self.history = []

        # Game Over state
        self.is_game_over = False
        self.game_over_reason = ""

    def run_week(self, actions):
        """
        Run one week of simulation.
        actions: dict containing:
          - water_in: float (inches of water to add this week)
          - transplant: bool (move outdoors)
          - harden_off: bool (prepare for outdoors)
          - scout: bool (look for pests)
          - sanitation: bool (clean up debris)
        """
        report = {
            'week': self.week,
            'daily_logs': [],
            'events': [],
            'status_end': ""
        }

        if self.plant.health <= 0:
            self.is_game_over = True
            self.game_over_reason = "Plant died."
            return report

        # 1. Handle One-Time Weekly Actions
        if actions.get('transplant'):
            if self.environment.is_indoors:
                self.environment.set_indoors(False)
                report['events'].append("ACTION: Transplanted seedlings outdoors.")
                # Transplant shock logic could go here
                self.plant.health -= 0.05
            else:
                report['events'].append("ACTION: Already outdoors.")

        if actions.get('sanitation'):
             # Reduces disease pressure (simplified by clearing active diseases somewhat)
             # In a full model, this would reduce 'inoculum pool'
             if "Early Blight" in self.pests.active_diseases:
                 # Chance to remove
                 self.pests.active_diseases.discard("Early Blight")
                 report['events'].append("ACTION: Sanitation performed. Infected leaves removed.")

        # 2. Schedule Irrigation
        # Simple heuristic: Water twice a week (Day 0 and Day 3)
        water_total = actions.get('water_in', 0.0)
        water_schedule = [0.0] * 7
        water_schedule[0] = water_total * 0.5
        water_schedule[3] = water_total * 0.5

        # 3. Daily Loop
        for day in range(7):
            # A. Weather
            w = self.environment.generate_daily_weather()

            # B. Soil Water Balance
            usage = self.plant.get_water_consumption()
            self.environment.update_soil_moisture(w, water_schedule[day], usage)

            # C. Plant Logic
            prev_stage = self.plant.bbch_stage
            self.plant.update_daily(w, self.environment.soil_moisture)

            if self.plant.bbch_stage != prev_stage:
                report['events'].append(f"PHENOLOGY: Plant advanced to Stage {self.plant.bbch_stage}")

            # D. Pests/Risks
            daily_events = self.pests.check_daily(self.plant, w, self.environment.soil_moisture)

            # Filtering events based on scouting
            if daily_events:
                if actions.get('scout'):
                    # Detailed report
                    for e in daily_events:
                        report['events'].append(f"Day {day+1}: {e}")
                else:
                    # Only show severe stuff? Or generic warning?
                    # For this prototype, show them but maybe mark as "Noticed by chance"
                    for e in daily_events:
                         report['events'].append(f"Day {day+1}: (UNSCOUTED) {e}")

            # E. Check Death
            if self.plant.health <= 0:
                self.is_game_over = True
                self.game_over_reason = "Plant health dropped to zero."
                break

            report['daily_logs'].append(f"Day {day+1}: {w} | Soil: {self.environment.soil_moisture:.2f}")

        self.week += 1
        report['status_end'] = self.plant.get_narrative_status()

        # Check Harvest success
        if self.plant.ripe_fruit_count > 0 and actions.get('harvest'):
            report['events'].append(f"HARVEST: Picked {self.plant.ripe_fruit_count} ripe fruits!")
            self.plant.ripe_fruit_count = 0 # Reset buffer

        return report
