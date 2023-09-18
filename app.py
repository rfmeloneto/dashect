import dash
import dash_bootstrap_components as dbc
import flask
import pandas as pd
import plotly.express as px
import requests
from dash import dcc, html
from dash.dependencies import Input, Output

server = flask.Flask(__name__)
app = dash.Dash(__name__, server, external_stylesheets=[dbc.themes.FLATLY])
server.config["MAX_CONTENT_LENGTH"] = 1024 * 1024 * 1024

df = pd.read_csv("urnas.csv")
dft = pd.read_csv("resultado.csv")


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
                                                    [
                                                        dbc.Row(
                                                            [
                                                                html.H5(
                                                                    "Total de Urnas Apuradas"
                                                                )
                                                            ]
                                                        ),
                                                        dbc.Row(
                                                            html.H5(id="total_urnas")
                                                        ),
                                                    ],
                                                    className="p-4 text-center shadow-sm",
                                                ),
                                                dbc.Card(
                                                    [
                                                        dbc.Row(
                                                            [
                                                                html.H5(
                                                                    "Total de Seções Apuradas"
                                                                )
                                                            ]
                                                        ),
                                                        dbc.Row(
                                                            html.H5(id="total_secoes")
                                                        ),
                                                    ],
                                                    className="p-4 text-center shadow-sm",
                                                ),
                                                dbc.Card(
                                                    [
                                                        dbc.Row(
                                                            [
                                                                html.H5(
                                                                    "Total de Votos Apurados"
                                                                )
                                                            ]
                                                        ),
                                                        dbc.Row(
                                                            html.H5(id="total_votos")
                                                        ),
                                                    ],
                                                    className="p-4 text-center shadow-sm",
                                                ),
                                            ]
                                        ),
                                        dbc.Col(
                                            [
                                                dbc.Card(
                                                    [
                                                        dbc.Row(
                                                            html.H5("Resultado"),
                                                        ),
                                                        dbc.Row(
                                                            dcc.Graph(id="resultado")
                                                        ),
                                                    ],
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
    response = requests.get(
        "https://raw.githubusercontent.com/tbrugz/geodata-br/master/geojson/geojs-17-mun.json"
    )
    geojson = response.json()
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


@app.callback(
    Output("total_urnas", "children"),
    Input("dropdown", "value"),
)
def update_total_urnas(value):
    return (dft[dft["cidade"] == value]["urnas_apuradas"].sum(),)


@app.callback(
    Output("total_secoes", "children"),
    Input("dropdown", "value"),
)
def update_total_secoes(value):
    return (dft[dft["cidade"] == value]["secoes_apuradas"].sum(),)


@app.callback(
    Output("total_votos", "children"),
    Input("dropdown", "value"),
)
def update_total_votos(value):
    return (dft[dft["cidade"] == value]["votos_apurados"].sum(),)


@app.callback(
    Output("resultado", "figure"),
    Input("dropdown", "value"),
)
def update_resultado(value):
    df_filtered = dft.drop(
        ["urnas_apuradas", "secoes_apuradas", "votos_apurados"], axis=1
    )
    df_city = df_filtered[df_filtered["cidade"] == value]
    non_empty_values = df_city.iloc[0].dropna()
    fig = px.pie(values=non_empty_values.values, names=non_empty_values.index)

    return fig


if __name__ == "__main__":
    app.run_server(debug=True)
