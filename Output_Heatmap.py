import json
import pandas as pd
from pathlib import Path
import plotly.express as px
from tkinter import Tk, filedialog
from datetime import datetime

def select_directory():
    root = Tk()
    root.withdraw()
    return filedialog.askdirectory(title="Select Folder with JSON Conflict Files")

def load_event_data(json_dir):
    data = []
    for file in Path(json_dir).glob("*.json"):
        try:
            with open(file, "r") as f:
                event = json.load(f)
                timestamp = event.get("eventDate", "") + "T" + event.get("eventTime", "")
                parsed_time = datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%S.%f")
                data.append({
                    "uniqueId": event.get("uniqueId"),
                    "eventScore": event.get("eventScore"),
                    "latitude": event.get("latitude"),
                    "longitude": event.get("longitude"),
                    "trueLateralNm": event.get("atEventTime", {}).get("trueLateralNm"),
                    "trueVerticalFt": event.get("atEventTime", {}).get("trueVerticalFt"),
                    "altitude_0": event.get("aircraft_0", {}).get("altitudeInFeet"),
                    "altitude_1": event.get("aircraft_1", {}).get("altitudeInFeet"),
                    "timestamp": parsed_time,
                    "date": parsed_time.date(),
                    "hour": parsed_time.hour
                })
        except Exception as e:
            print(f"Error reading {file.name}: {e}")
    return pd.DataFrame(data)

def plot_filtered_map(df):
    import plotly.graph_objects as go
    import plotly.express as px
    import dash
    from dash import dcc, html
    from dash.dependencies import Input, Output

    app = dash.Dash(__name__)
    app.title = "CPA Viewer"

    available_dates = sorted(df['date'].unique())
    min_hour, max_hour = df['hour'].min(), df['hour'].max()

    app.layout = html.Div([
        html.H1("Closest Point of Approach (CPA)", style={'textAlign': 'center'}),
        html.Div([
            html.Label("Select One or More Dates (or All):"),
            dcc.Dropdown(
                id='date-filter',
                options=[{"label": str(d), "value": str(d)} for d in available_dates],
                value=[str(d) for d in available_dates],
                multi=True
            ),
            html.Label("Hour Range:"),
            dcc.RangeSlider(
                id='hour-slider',
                min=min_hour,
                max=max_hour,
                value=[min_hour, max_hour],
                marks={i: f"{i}:00" for i in range(min_hour, max_hour+1, 1)},
                step=1
            )
        ], style={'width': '50%', 'margin': 'auto'}),

        dcc.Graph(id='heatmap', style={'height': '800px'})
    ])

    @app.callback(
        Output('heatmap', 'figure'),
        Input('date-filter', 'value'),
        Input('hour-slider', 'value')
    )
    def update_graph(selected_dates, hour_range):
        filtered = df[
            (df['date'].astype(str).isin(selected_dates)) &
            (df['hour'] >= hour_range[0]) &
            (df['hour'] <= hour_range[1])
        ]

        fig = px.scatter_mapbox(
            filtered,
            lat="latitude",
            lon="longitude",
            color="eventScore",
            color_continuous_scale=[(0, "red"), (0.5, "yellow"), (1, "green")],
            hover_data={
                "uniqueId": True,
                "eventScore": True,
                "latitude": True,
                "longitude": True,
                "trueLateralNm": True,
                "trueVerticalFt": True,
                "altitude_0": True,
                "altitude_1": True
            },
            labels={
                "eventScore": "Event Score",
                "trueLateralNm": "Lateral Separation NM",
                "trueVerticalFt": "Vertical Separation FT",
                "altitude_0": "Altitude A/C 0 (FT)",
                "altitude_1": "Altitude A/C 1 (FT)",
                "uniqueId": "Unique ID"
            },
            size="eventScore",
            size_max=12,
            zoom=8,
            title="Closest Point of Approach (CPA)",
            mapbox_style="carto-positron"
        )

        return fig

    app.run(debug=True)

if __name__ == "__main__":
    folder = select_directory()
    if folder:
        df = load_event_data(folder)
        if not df.empty:
            plot_filtered_map(df)
        else:
            print("No valid JSON data found.")
    else:
        print("No folder selected.")
