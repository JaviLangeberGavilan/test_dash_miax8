import dash
from dash import dcc
from dash import html
from dash.dependencies import Input, Output, State
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from utils import ApiBmeHandler


external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)


apih_ibex = ApiBmeHandler(market='IBEX')
apih_dax = ApiBmeHandler(market='DAX')
apih_euro = ApiBmeHandler(market='EUROSTOXX')


tck_ibex = list(apih_ibex.get_ticker_master()['ticker'])
tck_dax = list(apih_dax.get_ticker_master()['ticker'])
tck_euro = list(apih_euro.get_ticker_master()['ticker'])

styles={
    'title':{
        'background-color': 'black',
        'color': 'white',
        'text-align': 'center',
        'paadding': '70px',
    },
    'div-dropdowns':{
        'position': 'relative',
        'botom': '50px',
        'left': '200px',
        'padding': '40px',
        'border': '1px solid #BFBFBF',
        'background-color': 'white',
        'width': '50%',
    }
}

app.layout = html.Div(children=[
    html.Div([
        html.H1(children="mIA-X DATA EXPLORER"),
        html.H4(children="mIA-X API")
    ],
    style = styles['title']
    ),
    html.Div([
        html.Div([
            dcc.Dropdown(
                options=[
                    {"label": 'IBEX', "value": 'IBEX'},
                    {"label": 'DAX', "value": 'DAX'},
                    {"label": 'EUROSTOXX', "value": 'EUROSTOXX'}, 
                ],
                value="IBEX",
                id='dropdown-market'
            )
        ],
        style={'width': '40%', 'display': 'inline-block'}
        ),

        html.Div([
            dcc.Dropdown(id='dropdown-assets')
        ],
        style={'width': '40%', 'float': 'right', 'display': 'inline-block'}
        ),
    ],
    style=styles['div-dropdowns']),

    dcc.Graph(id="graph")
])


@app.callback(
    Output('dropdown-assets', 'options'),
    Input("dropdown-market", "value"),
)
def update_options(selected_market):
    if selected_market == 'IBEX':
        return [{'label': i, 'value': i} for i in tck_ibex]
    elif selected_market == 'DAX':
        return [{'label': i, 'value': i} for i in tck_dax]
    elif selected_market == 'EUROSTOXX':
        return [{'label': i, 'value': i} for i in tck_euro]


@app.callback(
    Output('dropdown-assets', 'value'),
    Input('dropdown-assets', 'options')
)
def select_first(options):
    return options[0]['value']


@app.callback(
    Output('graph', 'figure'),
    Input('dropdown-assets', 'value'),
    Input('dropdown-market', 'value'),
)
def update_graph(tck, market):
    if market == 'IBEX':
        df = apih_ibex.get_close_data_tck(tck, False)
    elif market == 'DAX':
        df = apih_dax.get_close_data_tck(tck, False)
    elif market == 'EUROSTOXX':
        df = apih_euro.get_close_data_tck(tck, False)

    fig = go.Figure(
        go.Candlestick(
            x = df.index,
            open = df['open'],
            high = df['high'],
            low = df['low'],
            close = df['close']
        )
    )
    return fig


if __name__ == '__main__':
    app.run_server(host="0.0.0.0", debug=False, port=8080)