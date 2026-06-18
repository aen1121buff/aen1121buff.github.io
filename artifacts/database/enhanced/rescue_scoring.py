"""
Rescue candidate scoring logic for CS 499 Milestone Three.

This file adds the algorithms and data structures enhancement. It converts the
client rescue requirements into reusable criteria dictionaries, scores each animal,
and sorts the result list so the strongest rescue candidates appear first.
"""

from typing import Any, Dict, List

RESCUE_CRITERIA: Dict[str, Dict[str, Any]] = {
    "water": {
        "label": "Water Rescue",
        "breeds": {"Labrador Retriever Mix", "Chesapeake Bay Retriever", "Newfoundland"},
        "sex": "Intact Female",
        "min_weeks": 26,
        "max_weeks": 156,
    },
    "mountain": {
        "label": "Mountain or Wilderness Rescue",
        "breeds": {"German Shepherd", "Alaskan Malamute", "Old English Sheepdog", "Siberian Husky", "Rottweiler"},
        "sex": "Intact Male",
        "min_weeks": 26,
        "max_weeks": 156,
    },
    "disaster": {
        "label": "Disaster Rescue or Individual Tracking",
        "breeds": {"Doberman Pinscher", "German Shepherd", "Golden Retriever", "Bloodhound", "Rottweiler"},
        "sex": "Intact Male",
        "min_weeks": 20,
        "max_weeks": 300,
    },
}


def build_query(rescue_type: str) -> Dict[str, Any]:
    """Build a MongoDB query for the selected rescue type."""
    if rescue_type == "reset" or rescue_type not in RESCUE_CRITERIA:
        return {}

    criteria = RESCUE_CRITERIA[rescue_type]
    return {
        "animal_type": "Dog",
        "breed": {"$in": sorted(criteria["breeds"])},
        "sex_upon_outcome": criteria["sex"],
        "age_upon_outcome_in_weeks": {"$gte": criteria["min_weeks"], "$lte": criteria["max_weeks"]},
    }


def _safe_age(animal: Dict[str, Any]) -> float:
    """Return age in weeks as a number, or 0 when the value cannot be used."""
    try:
        return float(animal.get("age_upon_outcome_in_weeks", 0))
    except (TypeError, ValueError):
        return 0


def score_animal(animal: Dict[str, Any], rescue_type: str) -> int:
    """Score one animal based on breed, age, sex, and outcome type.

    The score is intentionally simple and explainable. A machine learning model could
    be more complex, but this rule based approach is easier to audit and better fits
    the assignment goal of showing clear algorithmic reasoning.
    """
    if rescue_type not in RESCUE_CRITERIA:
        return 0

    criteria = RESCUE_CRITERIA[rescue_type]
    score = 0
    breed = animal.get("breed", "")
    sex = animal.get("sex_upon_outcome", "")
    outcome_type = animal.get("outcome_type", "")
    age = _safe_age(animal)

    if breed in criteria["breeds"]:
        score += 40

    if criteria["min_weeks"] <= age <= criteria["max_weeks"]:
        score += 30
        preferred_midpoint = (criteria["min_weeks"] + criteria["max_weeks"]) / 2
        age_distance = abs(age - preferred_midpoint)
        if age_distance <= 26:
            score += 10

    if sex == criteria["sex"]:
        score += 10

    if outcome_type in {"Adoption", "Transfer"}:
        score += 10

    return score


def rank_animals(animals: List[Dict[str, Any]], rescue_type: str) -> List[Dict[str, Any]]:
    """Add a rescue score to each record and sort records by score descending.

    Time complexity is O(n log n) because each animal is scored once and then the
    list is sorted. Space complexity is O(n) because new enriched records are built.
    """
    ranked = []
    for animal in animals:
        enriched_record = dict(animal)
        enriched_record["rescue_score"] = score_animal(animal, rescue_type)
        ranked.append(enriched_record)

    ranked.sort(
        key=lambda record: (
            record.get("rescue_score", 0),
            record.get("breed", ""),
            record.get("name", ""),
        ),
        reverse=True,
    )
    return ranked
