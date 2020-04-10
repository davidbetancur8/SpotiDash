# ===================================================================
# Importante tener el stylesheet.css dentro de el directorio assets
# ===================================================================

import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
import datetime
from dateutil.relativedelta import relativedelta
import plotly.graph_objs as go
from dash.dependencies import Output, Input, State
import pandas as pd
import plotly.express as px
import io
import requests
from urllib.request import urlopen
import json
import numpy as np
from spotipy.oauth2 import SpotifyClientCredentials
import spotipy
import time
import sys

client_credentials_manager = SpotifyClientCredentials()
sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)
sp.trace = False

colnames = [
    "popularity",
    "danceability",
    "energy",
    "speechiness",
    "acousticness",
    "instrumentalness",
    "liveness",
    "valence",
]



def get_features():
    song_name = "bohemian rhapsody"
    results = sp.search(q=song_name, limit=1)

    name = results["tracks"]["items"][0]["name"]
    artists = [t["name"] for t in results["tracks"]["items"][0]["artists"]]

    tids = results["tracks"]["items"][0]["uri"]
    features = sp.audio_features(tids)[0]

    vals = [

        results["tracks"]["items"][0]["popularity"],
        features["danceability"]*100,
        features["energy"]*100,
        features["speechiness"]*100,
        features["acousticness"]*100,
        features["instrumentalness"]*100,
        features["liveness"]*100,
        features["valence"]*100,
    ]
    df = pd.DataFrame(dict(r=vals,theta=colnames))
    return df, name, artists

def plot_features():
    df, name, artists = get_features()
    
    fig = px.line_polar(df, r='r', theta='theta', line_close=True)

    fig.update_layout(title=f"{name} ({' & '.join(artists)})",
                    font=dict(
                            family="Courier New, monospace",
                            size=15,
                            color="#7f7f7f"
                        ),
                )
    return fig




app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
server = app.server


app.layout = dbc.Container([
    html.Div([
        html.H2("Spotify Audio features", className="pretty_container", style={'text-align': 'center'})]
    ),

    html.Div([
        dcc.Input(
            id = "input_query",
            placeholder = "Search",
            type="text",
            value = "Bohemian Rhapsody",
            className = "pretty_container",
            style={'text-align': 'center'}
        ),
        html.Button("Search", id="button_search", className = "pretty_container")
    ],className="pretty_container", style={'text-align': 'center'}),

    html.Div([  dbc.Row([
                    html.Div(
                        dcc.Graph(
                            id = "audio_feats",
                            figure = plot_features()
                        ), className="pretty_container"
                    ),
                ]),
                
    ])


], fluid=True)



@app.callback(
    Output('audio_feats', 'figure'),
    [Input('button_search', 'n_clicks')],
    [State('input_query', 'value')])

def display_output(nclicks, input_query):
    results = sp.search(q=input_query, limit=1)
    name = results["tracks"]["items"][0]["name"]
    artists = [t["name"] for t in results["tracks"]["items"][0]["artists"]]

    tids = results["tracks"]["items"][0]["uri"]
    features = sp.audio_features(tids)[0]

    vals = [

        results["tracks"]["items"][0]["popularity"],
        features["danceability"]*100,
        features["energy"]*100,
        features["speechiness"]*100,
        features["acousticness"]*100,
        features["instrumentalness"]*100,
        features["liveness"]*100,
        features["valence"]*100,
    ]
    df = pd.DataFrame(dict(r=vals,theta=colnames))

    fig = px.line_polar(df, r='r', theta='theta', line_close=True, range_r=[0,100])

    fig.update_layout(title=f"{name} ({' & '.join(artists)})",
                    font=dict(
                            family="Courier New, monospace",
                            size=15,
                            color="#7f7f7f"
                        ),
                )
    return fig



if __name__ == "__main__":
    app.run_server(port=4070)
