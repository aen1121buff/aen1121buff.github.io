[README.md](https://github.com/user-attachments/files/29108030/README.md)
# CS 499 Milestone Three

Enhancement Two: Algorithms and Data Structure

Student: Anthony Cheung

## Artifact

The artifact is the CS 340 Grazioso Salvare dashboard. The original project used Python, MongoDB, Dash, Pandas, Plotly, and Dash Leaflet to help identify dogs from the Austin Animal Center dataset that may be useful for rescue training.

## Enhancement Summary

For Milestone Three, the main enhancement is a rescue suitability scoring algorithm. The original dashboard filtered records by rescue type, but the enhanced dashboard now scores each matching dog and sorts the results so the strongest rescue candidates appear first.

The enhancement includes:

1. A rescue criteria dictionary for water rescue, mountain or wilderness rescue, and disaster rescue or individual tracking.
2. A scoring function that assigns points for breed, age, sex, and outcome type.
3. A ranking function that stores scored records in a list and sorts them by rescue score.
4. Dashboard table updates that display the new rescue_score field.
5. A README and narrative explaining algorithmic design choices and tradeoffs.

## Files Included

* original_dashboard_reference.py
* animal_shelter.py
* rescue_scoring.py
* dashboard_enhanced.py
* requirements.txt
* README.md

## Algorithm Explanation

The rank_animals function scores every animal once, then sorts the enriched records by rescue_score. Scoring is O(n) because each record is evaluated once. Sorting is O(n log n). The total time complexity is O(n log n), and the space complexity is O(n) because a new ranked list is created.

## Why This Shows Algorithms and Data Structures

This enhancement uses dictionaries, sets, lists, conditionals, scoring rules, and sorting. The rescue criteria are stored in dictionaries and sets so the logic is easier to update. The result records are stored in a list and sorted with a custom key. This makes the dashboard more useful because users can compare candidates by ranked suitability instead of manually reading through unsorted records.

## How to Run

1. Load the Austin Animal Center data into MongoDB as database aac and collection animals.
2. Create a MongoDB user with read and write access.
3. Install the required Python packages with pip install minus r requirements.txt.
4. Run dashboard_enhanced.py.
5. Select a rescue type to view ranked candidates.

## Course Outcome Alignment

This enhancement mainly supports Course Outcome 3 because it designs and evaluates a computing solution using algorithmic principles, data structures, and tradeoff analysis. It also supports Course Outcome 2 because the narrative and README explain the enhancement in a professional way.
