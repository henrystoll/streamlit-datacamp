import json
import urllib.request
from datetime import timedelta

import pandas as pd
import streamlit as st
import altair as alt


@st.cache
def load_data():
    DATA_URL = "https://cbs2020-datacamp.azurewebsites.net/get_results"

    req = urllib.request.urlopen(DATA_URL).read()
    json_data = json.loads(req)['Results']
    # clean data
    df = pd.DataFrame(json_data)
    df = df.drop(columns=['email'])
    df['date'] = df['date'].apply(lambda s: s[:14] + "00:00")
    numeric_col = ['chapters_completed', 'courses_completed', 'xp']
    df[numeric_col] = df[numeric_col].apply(pd.to_numeric)
    df['date'] = pd.to_datetime(df['date'])
    # df = df[df['xp'] > 0]  # no values with null
    return df


st.title("Datacamp Leaderboard")
# Create a text element and let the reader know the data is loading.
data_load_state = st.text('Data loading...')
data = load_data()
# Notify the reader that the data was successfully loaded.
data_load_state.text("")
# data_load_state.text("Data cached")


# st.line_chart(data[['xp', 'name', 'date']])

st.sidebar.markdown("Interact with the data here")

max_xp = round(data['xp'].max() / 1000) * 1000
xp_slider = st.sidebar.slider('Minimum XP', 0, max_xp, 2000, 1000)

datetime_start = (data.iloc[300, 2]).to_pydatetime()
datetime_end = data.iloc[-1, 2].to_pydatetime()
date_slider = st.sidebar.slider('End Date', datetime_start, datetime_end, datetime_end, timedelta(hours=1))

# filtered = data[(data['xp'] > xp_slider) & (data['date'] < data.iloc[-94, 2])]
filtered = data[(data['xp'] > xp_slider) & (data['date'] < date_slider)]
c = alt.Chart(filtered).mark_line().encode(
    x='date', y='xp', color='name', tooltip=['date', 'xp', 'name'])

st.altair_chart(c, use_container_width=True)

st.subheader('Raw data')
st.write(filtered)
