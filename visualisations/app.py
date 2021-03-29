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
import plotly.graph_objects as go

from dash.dependencies import Input, Output


def load_db_credentials(json_path='../db_credentials.json'):
    with open(json_path) as f:
        return json.load(f)


external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

db_credentials = load_db_credentials()

conn1 = mariadb.connect(**db_credentials)
daily_df = pd.read_sql(f"SELECT * FROM daily_stats", conn1)
conn1.close()

# daily_df.loc[4:5, ['wakeup_time', 'online_today']] = None
daily_df['wakeup_time'] = daily_df['wakeup_time'].round().apply(pd.to_timedelta, unit='s') + pd.to_datetime(
    '1970/01/01')
daily_df['online_today'] = daily_df['online_today'].round().apply(pd.to_timedelta, unit='s') + pd.to_datetime(
    '1970/01/01')

day_order = {'day_name': ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']}
h24_on_plots = (pd.to_datetime('1970/01/01'), pd.to_datetime('1970/01/02'))
wakeup_time_boxplot = px.box(daily_df, x='day_name', y='wakeup_time', title=f'Wakeup time by weekday',
                             category_orders=day_order, range_y=h24_on_plots)
wakeup_time_boxplot.update_layout(title_x=.5)
time_online_boxplot = px.box(daily_df, x='day_name', y='online_today', title='Time online by weekday',
                             category_orders=day_order, range_y=h24_on_plots)
time_online_boxplot.update_layout(title_x=.5)


@app.callback(
    Output('memory', 'data'),
    Output('memory_today', 'data'),
    Input(component_id="interval-component", component_property="n_intervals")
)
def update_data(_, days_ago=2):
    conn = mariadb.connect(**db_credentials)
    start_of_yday = (datetime.datetime.today() - datetime.timedelta(days=days_ago)).strftime('%Y-%m-%d')
    data = pd.read_sql(f"SELECT * FROM lucjan_data WHERE date > '{start_of_yday}'", conn)
    start_of_today = datetime.datetime.today().strftime('%Y-%m-%d')
    today_data = pd.read_sql(f"SELECT * FROM lucjan_data WHERE date > '{start_of_today}'", conn)
    conn.close()
    return data.to_dict(), today_data.to_dict()


@app.callback(Output('timeseries_graph', 'figure'), Input('memory', 'data'))
def timeseries_graph_update(data):
    df = pd.DataFrame(data).astype({'date': 'datetime64', 'is_online': 'bool'})
    df.index = df.date
    df = df.rolling('1h').mean().reset_index()
    fig = px.line(df, x="date", y="is_online", hover_name="date", render_mode="svg",
                  title='Hourly mean of lucjan being online')
    fig.update_layout(uirevision='constant', title_x=.5)
    return fig


@app.callback(Output('pie_chart', 'figure'), Input('memory', 'data'))
def pie_chart(data):
    df = pd.DataFrame(data).astype({'date': 'datetime64', 'is_online': 'bool'})
    labels = ['online', 'offline']
    online = df['is_online'].sum()
    values = [online, df.shape[0] - online]

    fig = go.Figure(data=[go.Pie(labels=labels, values=values)])
    fig.update_layout(title_text="Percentage of time online", title_x=0.5)
    fig.update_layout(uirevision='constant')
    return fig


@app.callback(Output('time_online', 'children'), Input('memory_today', 'data'))
def time_online(today_data):
    df = pd.DataFrame.from_dict(today_data)
    return "Online today for " + (pd.Timedelta(f'{df["is_online"].sum()}m') + pd.Timestamp("00:00:00")).strftime(
        "%H:%M")


@app.callback(Output('wakeup_time', 'children'), Input('memory_today', 'data'))
def wakeup(today_data):
    df = pd.DataFrame(today_data).astype({'date': 'datetime64', 'is_online': 'bool'})
    for _, row in df.iterrows():
        s_passed = pd.Timedelta(row['date'].strftime('%H:%M:%S')).seconds
        if row['is_online'] and s_passed > 4*3600:
            return f'Wake up time {row["date"].strftime("%H:%M")} '
    return 'not on fb today, smart boi'


app.layout = html.Div(children=[
    html.H1(children='Is Lucjan online?', style={'textAlign': 'center'}),
    html.Label(id='time_online', style={'textAlign': 'center'}),
    html.Label(id='wakeup_time', style={'textAlign': 'center'}),

    html.Div([
        dcc.Graph(id='wakeup_time_boxplot', figure=wakeup_time_boxplot, className='four columns'),
        dcc.Graph(id='time_online_boxplot', figure=time_online_boxplot, className='four columns'),
        html.Div(dcc.Graph(id='pie_chart'), className='four columns')
    ], className='row'),

    dcc.Graph(id='timeseries_graph'),

    dcc.Interval(
        id='interval-component',
        interval=1 * 60000,  # in milliseconds
        n_intervals=0
    ),
    dcc.Store(id='memory'),
    dcc.Store(id='memory_today')
])

if __name__ == '__main__':
    app.run_server(debug=True)
