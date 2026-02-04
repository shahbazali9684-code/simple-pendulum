import sys
from src.simulation import SimulationEngine

def main():
    print("=== Week-by-Week Fruit Plant Simulation ===")
    print("Species: Tomato (Reference Scenario)")
    print("Goal: Grow from seed to harvest. Watch out for pests and weather!")
    print("You are starting indoors in early spring.")

    sim = SimulationEngine()

    while not sim.is_game_over:
        print(f"\n========================================")
        print(f"               WEEK {sim.week}")
        print(f"========================================")
        print(f"STATUS: {sim.plant.get_narrative_status()}")
        print(f"ENV:    {sim.environment.get_status()}")

        if sim.plant.ripe_fruit_count > 0:
            print(f"HARVEST READY: {sim.plant.ripe_fruit_count} fruits are ripe!")

        # User Inputs
        print("\nSelect Actions for the Week:")
        try:
            water_input = input("  Water amount (inches) [default 1.0]: ")
            water = float(water_input) if water_input.strip() else 1.0

            scout_input = input("  Scout for pests? (y/n) [default y]: ")
            scout = scout_input.lower() != 'n'

            transplant = False
            # Only offer transplant if indoors and plant is big enough (Stage > 10)
            if sim.environment.is_indoors and sim.plant.bbch_stage >= 10:
                transplant_input = input("  Transplant outdoors? (y/n) [default n]: ")
                transplant = transplant_input.lower() == 'y'

            sanitation = False
            # Sanitation relevant later
            if sim.week > 8:
                 sanitation_input = input("  Perform sanitation (prune/clean)? (y/n) [default n]: ")
                 sanitation = sanitation_input.lower() == 'y'

            harvest = False
            if sim.plant.ripe_fruit_count > 0:
                harvest_input = input("  Harvest ripe fruit? (y/n) [default y]: ")
                harvest = harvest_input.lower() != 'n'

        except ValueError:
            print("Invalid input detected. Using conservative defaults.")
            water = 1.0
            scout = True
            transplant = False
            sanitation = False
            harvest = True

        actions = {
            'water_in': water,
            'scout': scout,
            'transplant': transplant,
            'sanitation': sanitation,
            'harvest': harvest
        }

        print("\nSimulating week...")
        report = sim.run_week(actions)

        print("\n--- WEEKLY REPORT ---")
        print("Daily Weather Logs:")
        for log in report['daily_logs']:
            print("  " + log)

        if report['events']:
            print("\nMAJOR EVENTS:")
            for e in report['events']:
                print("  !!! " + e)
        else:
            print("\nNo major events this week.")

        print(f"\nEnd of Week Status: {report['status_end']}")

        # Season limit
        if sim.week > 24 and not sim.is_game_over:
            print("\nSeason End reached (Winter is coming).")
            sim.is_game_over = True
            sim.game_over_reason = "Season Completed."

    print("\n=== GAME OVER ===")
    print(f"Reason: {sim.game_over_reason}")
    print(f"Final Size: {sim.plant.height:.1f} cm")
    print(f"Total Biomass: {sim.plant.biomass:.1f}")

if __name__ == "__main__":
    main()
