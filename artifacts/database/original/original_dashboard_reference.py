"""
Original reference dashboard summary for CS 499 Milestone Three.

This file is included only as a reference version for submission. The original CS 340
project used a Python Dash dashboard connected to MongoDB through an AnimalShelter
CRUD module. It filtered animals by rescue type and updated a table, chart, and map.

The Milestone Three enhanced version adds rescue scoring and ranked sorting.
"""

from animal_shelter import AnimalShelter

username = "aacuser"
password = "SNHU1234"
db = AnimalShelter(username, password)

# Original style behavior: read records directly and display them without a score.
records = db.read({})
print(f"Loaded {len(records)} animal records from MongoDB.")
