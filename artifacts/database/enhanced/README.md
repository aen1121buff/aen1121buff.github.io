[README.md](https://github.com/user-attachments/files/29108371/README.md)
# CS 499 Milestone Four

Enhancement Three: Databases

Student: Anthony Cheung

## Artifact

The artifact is the CS 340 Grazioso Salvare dashboard. The project uses Python, MongoDB, Dash, Pandas, Plotly, and Dash Leaflet to display animal shelter records from the Austin Animal Center dataset. The dashboard helps Grazioso Salvare identify dogs that may be good candidates for rescue training.

This Milestone Four submission builds on the Milestone Three files. Milestone Three added rescue scoring and ranked sorting. Milestone Four keeps that work and adds database focused improvements to the MongoDB access layer and dashboard data retrieval.

## Enhancement Summary

The database enhancement improves how the application connects to MongoDB, validates queries, retrieves filtered records, and supports dashboard performance.

The enhancement includes:

1. Connection validation using a MongoDB ping before dashboard queries run.
2. Environment variable support for database configuration.
3. Safer validation for create, read, update, delete, projection, and sorting inputs.
4. Controlled dashboard projections so the dashboard only retrieves the fields it needs.
5. Index creation for fields used by rescue filters and scoring logic.
6. Count and distinct helper methods for reporting and database checking.
7. An aggregation helper method for future reporting views.
8. Safer delete behavior that deletes one record by default unless many record deletion is specifically allowed.
9. A database test script that checks connection, indexes, counts, and sample filtered records.

## Files Included

* original_dashboard_reference.py
* animal_shelter.py
* rescue_scoring.py
* dashboard_enhanced.py
* database_tests.py
* requirements.txt
* README.md

## Enhanced Files

### animal_shelter.py

This is the main database enhancement file. It improves the reusable MongoDB CRUD class by adding connection checks, input validation, controlled projection support, indexed filter fields, count, distinct, aggregation, dashboard record retrieval, and safer update and delete behavior.

### dashboard_enhanced.py

This file was updated to use the improved database access layer. The dashboard now requests only the fields it needs, uses the database count method, displays index status, caps dashboard reads for faster display, and still applies the Milestone Three rescue ranking logic.

### database_tests.py

This file gives a simple way to test the database enhancement without opening the full dashboard. It validates the connection, creates indexes, checks counts, and prints sample records for one rescue filter.

### README.md

This file explains the database enhancement, files, run steps, and course outcome alignment.

## How to Run

1. Load the Austin Animal Center data into MongoDB as database `aac` and collection `animals`.
2. Create a MongoDB user with read and write access.
3. Install the required Python packages with `pip install -r requirements.txt`.
4. Run `python database_tests.py` to confirm the database connection and index setup.
5. Run `python dashboard_enhanced.py` to start the dashboard.
6. Select a rescue type to view filtered and ranked rescue candidates.

Optional environment variables:

* AAC_USERNAME
* AAC_PASSWORD
* AAC_HOST
* AAC_PORT
* AAC_DATABASE
* AAC_COLLECTION
* AAC_AUTH_SOURCE

## Course Outcome Alignment

This enhancement mainly supports Course Outcome 4 because it uses MongoDB, Python, Dash, and database design practices to improve a computing solution that delivers value. It also supports Course Outcome 5 because the improved database layer uses validation, safer update and delete behavior, and controlled field retrieval to reduce database risk. The README and narrative also support Course Outcome 2 by explaining the technical improvement in a professional way.
