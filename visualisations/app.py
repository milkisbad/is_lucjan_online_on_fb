# -*- coding: utf-8 -*-

# Run this app with `python app.py` and
# visit http://127.0.0.1:8050/ in your web browser.

import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.express as px
import pandas as pd
import datetime
import json
import mariadb

def load_db_credentials(json_path='db_credentails.json'):
    with open('db_credentials.json') as f:
        return json.load(f)

def wakeup(df):
    for _, row in df.iterrows():
        if row['is_online']:
            return f'Lucjan has woken up at {str(row["date"].strftime("%H:%M"))} today'
            break
    return 'not on fb today, smart boi'

def time_online(df):
    return "Online today for " + (pd.Timedelta(f'{df["is_online"].sum()}m')+ pd.Timestamp("00:00:00")).strftime("%H:%M") + " hours total"

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

# assume you have a "long-form" data frame
# see https://plotly.com/python/px-arguments/ for more options
db_credentials = load_db_credentials()

conn = mariadb.connect(**db_credentials)
df = pd.read_sql("SELECT * FROM lucjan_data_bakap", conn)

# df = pd.read_csv('../data/lucjan_data.csv',  parse_dates=[0])

start_of_today = datetime.datetime.today().strftime('%Y-%m-%d')
today_df = df[df['date']>start_of_today]

fig = px.line(df, x="date", y="is_online", hover_name="date", render_mode="svg")
pie = px.pie(df, names='is_online', title='Percentage of time online')

wakeup_today = wakeup(today_df)
time_online_today = time_online(today_df)

app.layout = html.Div(children=[
    html.H1(children='Is Lucjan online?', style={'textAlign': 'center'}),

    html.Div(children=f'{wakeup_today}', style={
        'textAlign': 'center'
    }),

    html.Div(children=f'{time_online_today}', style={
        'textAlign': 'center'
    }),

    dcc.Graph(
        id='histogram',
        figure=pie
    ),

    dcc.Graph(
        id='timeseries',
        figure=fig
    )


])


if __name__ == '__main__':
    app.run_server(debug=True)