# -*- coding: utf-8 -*-

# Run this app with `python app.py` and
# visit http://127.0.0.1:8050/ in your web browser.

import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.express as px
import pandas as pd
import datetime

def wakeup(df):
    for _, row in df.iterrows():
        if row['is_online']:
            return f'Lucjan has woken up at {str(row["date"].strftime("%H:%M"))} today'
            break
    return 'not on fb today, smart boi'

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

# assume you have a "long-form" data frame
# see https://plotly.com/python/px-arguments/ for more options
df = pd.read_csv('../data/lucjan_data.csv',  parse_dates=[0])
# df = pd.DataFrame({
#     "Fruit": ["Apples", "Oranges", "Bananas", "Apples", "Oranges", "Bananas"],
#     "Amount": [4, 1, 2, 2, 4, 5],
#     "City": ["SF", "SF", "SF", "Montreal", "Montreal", "Montreal"]
# })

# fig = px.bar(df, x="Fruit", y="Amount", color="City", barmode="group")
fig = px.line(df, x="date", y="is_online", hover_name="date", render_mode="svg")
pie = px.pie(df, names='is_online', title='Percentage of time online')

start_of_today = datetime.datetime.today().strftime('%Y-%m-%d')
wakeup_today = wakeup(df[df['date']>start_of_today])

app.layout = html.Div(children=[
    html.H1(children='Is Lucjan online?', style={'textAlign': 'center'}),

    html.Div(children=f'{wakeup_today}', style={
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