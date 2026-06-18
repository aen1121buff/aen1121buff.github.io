"""
Enhanced CS 340 Grazioso Salvare dashboard for CS 499 Milestone Four.

This version keeps the Milestone Three rescue ranking algorithm and adds database
focused improvements. The dashboard now requests a controlled set of fields from
MongoDB, uses indexed filter fields, displays the database count for each filter,
and handles database errors in the user interface.
"""

from dash import Dash, dcc, html, dash_table
from dash.dependencies import Input, Output
import dash_leaflet as dl
import pandas as pd
import plotly.express as px

from animal_shelter import AnimalShelter
from rescue_scoring import RESCUE_CRITERIA, build_query, rank_animals

USERNAME = "aacuser"
PASSWORD = "SNHU1234"
MAX_DASHBOARD_RECORDS = 500

shelter = AnimalShelter(USERNAME, PASSWORD)
try:
    INDEX_STATUS = f"Database indexes ready: {', '.join(shelter.create_filter_indexes())}"
except RuntimeError as error:
    INDEX_STATUS = f"Database index check failed: {error}"

app = Dash(__name__)


def get_ranked_dataframe(rescue_type: str) -> pd.DataFrame:
    """Read database records, score them, and return dashboard ready data."""
    query = build_query(rescue_type)
    records = shelter.get_dashboard_records(query, limit=MAX_DASHBOARD_RECORDS)
    ranked_records = rank_animals(records, rescue_type)
    dataframe = pd.DataFrame.from_records(ranked_records)
    if "_id" in dataframe.columns:
        dataframe = dataframe.drop(columns=["_id"])
    return dataframe


def build_filter_options():
    options = [{"label": "Reset", "value": "reset"}]
    for key, criteria in RESCUE_CRITERIA.items():
        options.append({"label": criteria["label"], "value": key})
    return options


def count_records(rescue_type: str) -> int:
    """Return the database count for the selected rescue filter."""
    query = build_query(rescue_type)
    return shelter.count(query)


starting_df = get_ranked_dataframe("reset")

app.layout = html.Div([
    html.H1("Grazioso Salvare Rescue Candidate Dashboard"),
    html.Div("Created by Anthony Cheung"),
    html.Div(INDEX_STATUS, id="index-status"),
    html.Hr(),
    html.Label("Select a rescue type"),
    dcc.RadioItems(
        id="rescue-filter",
        options=build_filter_options(),
        value="reset",
        inline=True,
    ),
    html.Div(id="record-count"),
    html.Hr(),
    dash_table.DataTable(
        id="datatable-id",
        columns=[{"name": column, "id": column, "deletable": False, "selectable": True} for column in starting_df.columns],
        data=starting_df.to_dict("records"),
        page_size=10,
        sort_action="native",
        filter_action="native",
        row_selectable="single",
        selected_rows=[0],
        style_table={"overflowX": "auto"},
        style_cell={"textAlign": "left", "fontFamily": "Arial", "fontSize": "12px"},
    ),
    html.Br(),
    html.Div(
        style={"display": "flex", "gap": "20px"},
        children=[
            html.Div(id="graph-id", style={"width": "50%"}),
            html.Div(id="map-id", style={"width": "50%"}),
        ],
    ),
])


@app.callback(
    [Output("datatable-id", "data"), Output("datatable-id", "columns"), Output("record-count", "children")],
    [Input("rescue-filter", "value")],
)
def update_table(rescue_type):
    try:
        dataframe = get_ranked_dataframe(rescue_type)
        columns = [{"name": column, "id": column, "deletable": False, "selectable": True} for column in dataframe.columns]
        label = "all animals" if rescue_type == "reset" else RESCUE_CRITERIA[rescue_type]["label"]
        db_count = count_records(rescue_type)
        count_message = (
            f"Showing {len(dataframe)} of {db_count} database records for {label}. "
            f"Dashboard reads are capped at {MAX_DASHBOARD_RECORDS} records for faster display. "
            "Ranked results show strongest candidates first."
        )
        return dataframe.to_dict("records"), columns, count_message
    except Exception as error:
        return [], [], f"Database read failed: {error}"


@app.callback(Output("graph-id", "children"), [Input("datatable-id", "data")])
def update_chart(view_data):
    dataframe = pd.DataFrame(view_data)
    if dataframe.empty or "breed" not in dataframe.columns:
        return html.Div("No chart data available.")
    top_breeds = dataframe["breed"].value_counts().head(10).reset_index()
    top_breeds.columns = ["breed", "count"]
    figure = px.bar(top_breeds, x="breed", y="count", title="Top Breeds in Current Results")
    return dcc.Graph(figure=figure)


@app.callback(Output("map-id", "children"), [Input("datatable-id", "data"), Input("datatable-id", "selected_rows")])
def update_map(view_data, selected_rows):
    dataframe = pd.DataFrame(view_data)
    if dataframe.empty or not selected_rows:
        return html.Div("Select a row to view map data.")

    row = selected_rows[0]
    if row >= len(dataframe):
        row = 0

    animal = dataframe.iloc[row]
    try:
        latitude = float(animal.get("location_lat", 30.75))
        longitude = float(animal.get("location_long", -97.48))
    except (TypeError, ValueError):
        latitude, longitude = 30.75, -97.48

    name = animal.get("name", "Unknown")
    breed = animal.get("breed", "Unknown breed")
    score = animal.get("rescue_score", 0)

    return dl.Map(
        style={"width": "100%", "height": "500px"},
        center=[latitude, longitude],
        zoom=10,
        children=[
            dl.TileLayer(),
            dl.Marker(
                position=[latitude, longitude],
                children=[dl.Tooltip(f"{name} | {breed} | Score: {score}")],
            ),
        ],
    )


if __name__ == "__main__":
    app.run_server(debug=True)
