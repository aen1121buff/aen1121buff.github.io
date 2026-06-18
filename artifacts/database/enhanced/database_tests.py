"""
Lightweight database validation checks for CS 499 Milestone Four.

These checks are optional, but they show the enhanced AnimalShelter database
methods without starting the Dash dashboard.
"""

from animal_shelter import AnimalShelter
from rescue_scoring import build_query


def main() -> None:
    shelter = AnimalShelter()
    print("MongoDB connection:", shelter.ping())
    print("Indexes:", shelter.create_filter_indexes())
    print("Total records:", shelter.count({}))

    water_query = build_query("water")
    print("Water rescue record count:", shelter.count(water_query))

    sample = shelter.get_dashboard_records(water_query, limit=3)
    print("Sample dashboard records:", len(sample))
    for record in sample:
        print(record.get("animal_id"), record.get("breed"), record.get("name"))

    shelter.close()


if __name__ == "__main__":
    main()
