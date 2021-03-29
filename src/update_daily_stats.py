import json
import mariadb
import datetime
import pandas as pd

with open('../db_credentials.json') as f:
    db_credentials = json.load(f)


def wakeup(df):
    for _, row in df.iterrows():
        s_passed = pd.Timedelta(row['date'].strftime('%H:%M:%S')).seconds
        if row['is_online'] and s_passed > 5 * 3600:
            return s_passed


def online_today(df):
    return pd.Timedelta(f'{df["is_online"].sum()}m').seconds


def take_last_day_and_calculate_daily_stats():
    start_of_today = datetime.datetime.today().strftime('%Y-%m-%d')
    start_of_yesterday = (datetime.datetime.today() - datetime.timedelta(days=1)).strftime('%Y-%m-%d')

    conn = mariadb.connect(**db_credentials)

    last_day_df = pd.read_sql(
        f"SELECT * FROM lucjan_data WHERE date BETWEEN '{start_of_yesterday}' AND '{start_of_today}'", conn)
    insert_row = datetime.datetime.strptime(start_of_yesterday, '%Y-%m-%d'), wakeup(last_day_df), online_today(
        last_day_df), pd.to_datetime(start_of_yesterday).strftime('%A')

    cur = conn.cursor()
    cur.execute("INSERT INTO daily_stats_1 (date, wakeup_time, online_today, day_name) VALUES (?, ?, ?, ?)", insert_row)
    conn.commit()
    conn.close()
    return insert_row


if __name__ == "__main__":
    take_last_day_and_calculate_daily_stats()
