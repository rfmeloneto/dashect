import dash
import dash_bootstrap_components as dbc
import flask
import pandas as pd
import plotly.express as px
from dash import dcc, html
from dash.dependencies import Input, Output

server = flask.Flask(__name__)
app = dash.Dash(__name__, server, external_stylesheets=[dbc.themes.FLATLY])
server.config["MAX_CONTENT_LENGTH"] = 1024 * 1024 * 1024

df = pd.read_csv("urnas.csv")
geojson_data = "TOgeojs.json"


app.layout = html.Div(
    [
        dbc.Row(
            dcc.Dropdown(
                id="dropdown",
                options=[
                    {"label": cidade, "value": cidade}
                    for cidade in df["cidade"].unique()
                ],
                value="Palmas",
                className="p-4",
            ),
        ),
        html.Br(),
        dbc.Row(
            [
                dbc.Col(
                    [
                        dbc.Card(
                            [
                                dbc.Row(
                                    [html.H4(id="nome_cidade")],
                                    className="p-4 text-center",
                                ),
                                dbc.Row(
                                    [
                                        dbc.Col(
                                            [
                                                dbc.Card(
                                                    html.H5("Total de Urnas Apuradas"),
                                                    className="p-4 text-center shadow-sm",
                                                ),
                                                dbc.Card(
                                                    html.H5("Total de Seções Apuradas"),
                                                    className="p-4 text-center shadow-sm",
                                                ),
                                                dbc.Card(
                                                    html.H5("Total de Votos Apurados"),
                                                    className="p-4 text-center shadow-sm",
                                                ),
                                            ]
                                        ),
                                        dbc.Col(
                                            [
                                                dbc.Card(
                                                    html.H5("Resultado"),
                                                    className="p-4 text-center shadow-sm",
                                                )
                                            ]
                                        ),
                                    ]
                                ),
                            ]
                        )
                    ],
                    className="p-4",
                ),
                dbc.Col(
                    [
                        dcc.Graph(id="map"),
                    ]
                ),
            ]
        ),
    ],
    style={
        "background-color": "#f5f5f5",
        "height": "100vh",
        "width": "100%",
        "margin": 0,
        "padding": 0,
    },
)


@app.callback(Output("map", "figure"), Input("dropdown", "value"))
def update_map(selected_variable):
    with open(geojson_data, "r") as file:
        geojson = file.read()

    fig = px.choropleth_mapbox(
        df,
        geojson=geojson,
        locations="cidade",
        featureidkey="properties.name",
        color="urnas",
        hover_name="cidade",
        title="Mapa do Tocantins",
        color_continuous_scale="Viridis",
        opacity=1,
        mapbox_style="carto-positron",
        zoom=5,
        center={"lat": -10.1837, "lon": -48.3338},
    )

    fig.update_geos(
        visible=True,
        resolution=110,
        showcountries=False,
        showcoastlines=False,
        showland=False,
        fitbounds="locations",
    )

    fig.update_layout(
        margin={"r": 0, "t": 0, "l": 0, "b": 0},
        coloraxis_colorbar=dict(title="Contagem de Urnas"),
    )

    return fig


@app.callback(Output("nome_cidade", "children"), Input("dropdown", "value"))
def update_nome_cidade(value):
    return value


if __name__ == "__main__":
    app.run_server(debug=True)
