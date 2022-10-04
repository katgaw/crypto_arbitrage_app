print("{}".format(__name__))

import pandas as pd
import numpy as np
import pandas as pd
from Utilities import utils as u
import dash
from dash import Dash, dcc, html, Input, Output
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Upload dataset
dataset=pd.read_csv('Data/crypto_exchanges.csv', index_col='date1', parse_dates=True,infer_datetime_format=True)
profitable_arbitrage_btc=pd.read_csv('./Data/profitable_arbitrage_btc.csv',index_col='date1',infer_datetime_format=True,parse_dates=True)
profitable_arbitrage_dot=pd.read_csv('./Data/profitable_arbitrage_dot.csv',index_col='date1',infer_datetime_format=True,parse_dates=True)
exchange_coin_pos=pd.read_csv('./Data/exchange_coin_pos.csv',index_col='coin')
symbols_all=['BTC','ETH','SOL','DOT']

#Plot the dataset
df=dataset.groupby('coin').get_group(symbols_all[0]).iloc[:,1:]
df_heatmap=exchange_coin_pos.groupby('coin').get_group(symbols_all[0]).reset_index().iloc[:,1:]
df_heatmap.set_index('exchanges',inplace=True)
chart1 = make_subplots(rows=1, cols=2)

for col in df.columns[1:]:
    chart1.add_trace(go.Scatter(x=df.index,y=df[col],name=col),row=1,col=1)

fig_img=px.imshow(df_heatmap)
chart1.add_trace(fig_img.data[0],row=1,col=2)
chart1.update_layout({'plot_bgcolor':'LightGrey'}, height=500)
chart1.update_layout(legend=dict(orientation="h",
    yanchor="bottom",
    y=1,
    xanchor="right",
    x=1,
    font_size=10,
    font_color='black',
    ))

chart2 = go.Figure()
chart2.add_trace(
    go.Scatter(x=profitable_arbitrage_btc.index,y=profitable_arbitrage_btc['cumulative'],name='cum_profit_btc'))
chart2.add_trace(
    go.Scatter(x=profitable_arbitrage_dot.index,y=profitable_arbitrage_dot['cumulative'],name='cum_profit_polkadot'))
chart2.update_layout({'plot_bgcolor':'LightGrey'},height=500)

chart3 = go.Figure()
chart3.add_trace(
    go.Scatter(x=profitable_arbitrage_btc.index,y=profitable_arbitrage_btc['profit'],name='profit_btc'))
chart3.add_trace(
    go.Scatter(x=profitable_arbitrage_dot.index,y=profitable_arbitrage_dot['profit'],name='profit_polkadot'))
chart3.update_layout({'plot_bgcolor':'LightGrey'},height=500)

#################### Creating App Object ############################             
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = Dash(__name__, external_stylesheets=external_stylesheets)
server = app.server

colors = {
    'background': '#111111',
    'text': '#7FDBFF'
}

graph1 = dcc.Graph(
        id='graph1',
        figure=chart1,
        style={"height": "80%", "width": "90%"})

graph2 = dcc.Graph(
        id='graph2',
        figure=chart2,
        style={"height": "100%", "width": "100%"}
    )

graph3 = dcc.Graph(
        id='graph3',
        figure=chart3,
        style={"height": "100%", "width": "100%"}
    )
############### Creating Widgets #########################
multi_select_line_chart = dcc.Dropdown(
        id="multi_select_line_chart",
        options=[{"value":label, "label":label} for label in symbols_all],
        value=symbols_all[0],
        multi=True,
        clearable = True
    )    
header = html.H2(children="Crypto Arbitrage")
############### Setting App Layout ########################################

app.layout = html.Div([
    html.Div(children=[header], style={"text-align": "center", "justifyContent":"center", "background":"white"}),
    html.Div(
        className="row",
        children=[
            html.Div(
                className="twelve columns",
                children=[
                    html.Div(
                        children=[multi_select_line_chart])])]),
    html.Div(
        className="row",
        children=[
            html.Div(
                className="twelve columns bg-grey",
                children=[
                    html.Div(
                        children=[graph1])])]),
    html.Div(
        className="row",
        children=[
            html.Div(
                className="twelve columns bg-grey",
                children=[
                    html.Div(
                        children=[graph2])])]),
    html.Div(
        className="row",
        children=[
            html.Div(
                className="twelve columns bg-grey",
                children=[
                    html.Div(
                        children=[graph3])])])])

################## Creating Callbacks for the Widget ############################
@app.callback(Output('graph1', 'figure'),
 Input('multi_select_line_chart', 'value'))

def update_line(symbols_all):
    for symbol in symbols_all:
        df_heatmap=exchange_coin_pos.groupby('coin').get_group(symbol).reset_index().iloc[:,1:]
        df_heatmap.set_index('exchanges',inplace=True)
        df=dataset.groupby('coin').get_group(symbol).iloc[:,1:]
        chart1 = make_subplots(rows=1, cols=2)
        for col in df.columns[1:]:
            chart1.add_trace(go.Scatter(x=df.index,y=df[col],name=col),row=1,col=1)

        fig_img=px.imshow(df_heatmap)
        chart1.add_trace(fig_img.data[0],row=1,col=2)
        chart1.update_layout({'plot_bgcolor':'LightGrey'}, height=500)
        chart1.update_layout(legend=dict(orientation="h",
        yanchor="bottom",
        y=1,
        xanchor="right",
        x=1,
        font_size=10,
        font_color='black',
        ))
    return (chart1)



if __name__=='__main__':
    app.run_server(debug=True)