from dotenv import load_dotenv
import pandas as pd
import os
import streamlit as st
import plotly.express as px
import google.generativeai as genai
from datetime import datetime, timedelta
from main import retrieve_run_data

load_dotenv()

# Configure the API key
genai.configure(api_key=os.environ["GOOGLE_API_KEY"])

# Create a Gemini Pro model
gemini = genai.GenerativeModel('gemini-pro')

# function to retrieve latest run data from strava
retrieve_run_data()

# function to get current and past week's data in order to generate and get response from gemini
@st.cache_data
def coach_reccomendation(runs, weekly_data):
    # AI Recommendation 
    prev_week_df = runs[runs['start_week'] == list(weekly_data.get('Week'))[-2]]
    prev_total_distance = round(prev_week_df['distance'].sum(), 2)
    prev_num_runs = len(prev_week_df)
    prev_avg_heartrate = prev_week_df['average_heartrate'].mean()
    prev_avg_cadence = prev_week_df['average_cadence'].mean()

    current_week_df = runs[runs['start_week'] == list(weekly_data.get('Week'))[-1]]
    current_total_distance = round(current_week_df['distance'].sum(), 2)
    current_num_runs = len(current_week_df)
    current_avg_heartrate = current_week_df['average_heartrate'].mean()
    current_avg_cadence = current_week_df['average_cadence'].mean()

    query = f"""
    I want you to act like my running coach. I am going to give you data for runs in in my current week and my previous week.
    I want you to give me a comprehensive analysis/overview of my performance comparing the two weeks and give recommendations
    on the upcoming week. My goal is to participate in a race and improve general fitness.
    Last week, I ran {prev_num_runs} times throughout the week. I ran a total of {prev_total_distance} km 
    and I had an average heart rate of {prev_avg_heartrate} BPM and an average cadence of {prev_avg_cadence} SPM. 
    This week, I ran {current_num_runs} times throughout the week. I ran a total of {current_total_distance} km 
    and I had an average heart rate of {current_avg_heartrate} BPM. and an average cadence of {current_avg_cadence} SPM. 
    Have a positive and encouraging tone. Include the data provided in your response but keep it relatively concise.
    """
    response = gemini.generate_content(query)
    return response.text

st.set_page_config(page_title='Exclusive Run Club')
st.title('Very Exclusive Run Club 🏃')
st.markdown("<br>", unsafe_allow_html=True)
st.write('## Weekly kilometres')
st.markdown(':green[ ***A visualisation of your total weekly distance. Adjust the slider to change the number of weeks shown*** ]')
st.divider()


# Initialising dataframe
df = pd.read_csv('runData.csv') # loading csv into dataframe
runs = df[['name', 'distance', 'moving_time', 'start_date_local', 'average_cadence', 'average_heartrate']] # only getting distance, time and date of runs
runs['start_date_local'] = pd.to_datetime(runs['start_date_local']) # turning date into datetime object

# Getting time, distance and pace stats
# Data pre-processing and data wrangling
runs['stride_length'] = round(runs['distance'] / (runs['moving_time'] / 60 * runs['average_cadence'] * 2), 2)
runs['distance'] = round(runs['distance'] / 1000, 2)
runs['minutes'] = runs['moving_time'] // 60 
runs['seconds'] = runs['moving_time'] % 60
runs['pace_minutes'] = runs['moving_time'] / runs['distance'] // 60
runs['pace_seconds'] = round(runs['moving_time'] / runs['distance'] / 60 % 1 * 60)
runs['start_week'] = runs['start_date_local'].dt.to_period('W')
runs['start_week'] = pd.to_datetime(runs['start_week'].astype(str).str.split('/').str[0]).dt.strftime('Week of %b %d \'%y')
runs['time'] = runs['minutes'].astype(str).str.zfill(2) + ':' + runs['seconds'].astype(str).str.zfill(2)
runs['pace'] = runs['pace_minutes'].astype(int).astype(str) + ':' + runs['pace_seconds'].astype(int).astype(str).str.zfill(2)
runs['start_date_local'] = runs['start_date_local'].dt.strftime('%d-%m-%Y')
runs['average_cadence'] = round(runs['average_cadence'] * 2)


# final table to be displayed 
final = runs.drop(columns=['minutes', 'seconds', 'pace_minutes', 'pace_seconds', 'start_week', 'moving_time'])

# Grouping runs by weeks, and summing the distances for each week
weekly_mileage = runs.groupby('start_week')['distance'].sum().reset_index()

# slider for weeks in the year 
num_weeks = st.slider('Number of weeks:', min_value=5, max_value=52, value=5)

# generate range of dates for the past num_weeks, starting from current week
current_date = datetime.now()
current_week = current_date - timedelta(days=current_date.weekday())
week_dates = [current_week - timedelta(weeks=i) for i in range(num_weeks)] # get all n weeks starting from today and going backwards
week_dates.reverse()

# Create a dataframe with weeks and distances: all weeks that are not in run df, are assigned a value of zero
weekly_data = {'Week': [], 'Distance': []}
for week_date in week_dates:
    week_str = week_date.strftime('Week of %b %d \'%y')
    # if week is in the run database assign it the distance
    if week_str in weekly_mileage['start_week'].values:
        distance = weekly_mileage.loc[weekly_mileage['start_week'] == week_str, 'distance'].iloc[0] 
    # if week is not in run database, assign it zero
    else:
        distance = 0
    weekly_data['Week'].append(week_str)
    weekly_data['Distance'].append(distance)

# convert into dataframe
display_num_weeks = pd.DataFrame(weekly_data)

# Plotting weekly kilometres into a column graph and displaying it
column_graph = px.bar(display_num_weeks, x='Week', y='Distance', title='Mileage', height=600, width=800)
column_graph.update_traces(hovertemplate='%{y}km') # customising hover text 
column_graph.update_traces(marker_color='#FF9999') # customing colour
# Customize text size in layout
column_graph.update_layout(
    title={'font': {'size': 24}},  # Title text size
    xaxis={'title': {'text': 'Week', 'font': {'size': 18}},  # X-axis label text size
           'tickfont': {'size': 14}},  # X-axis tick text size
    yaxis={'title': {'text': 'Distance (km)', 'font': {'size': 18}},  # Y-axis label text size
           'tickfont': {'size': 14}}  # Y-axis tick text size
)

# displaying table and graph in streamlit
st.plotly_chart(column_graph)
st.divider()

# dropdown menu to select a particular week
st.write('## Weekly Run Statistics')
st.markdown(':green[ ***A weekly overview of your runs. Select a week from the dropdown to preview that week\'s runs and stats.*** ]')
select_week = st.selectbox('Select a week:', options=weekly_data.get('Week'))

selected_index = weekly_data.get('Week').index(select_week)

# calculate statistics for the selected week
selected_week_df = runs[runs['start_week'] == select_week]
selected_total_distance = round(selected_week_df['distance'].sum(), 2)
selected_num_runs = len(selected_week_df)
selected_total_time = selected_week_df['moving_time'].sum() // 60
selected_avg_heartrate = round(selected_week_df['average_heartrate'].mean())
selected_avg_cadence = round(selected_week_df['average_cadence'].mean())

selected_week_df = selected_week_df.drop(columns=['minutes', 'seconds', 'pace_minutes', 'pace_seconds', 'start_week', 'moving_time'])

st.dataframe(selected_week_df, width=800)

# displaying weekly statistics
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric(label="**Total Distance**", value=f"{selected_total_distance} km")
with col2: 
    st.metric(label="**Total time**", value=f"{selected_total_time} mins")
with col3: 
    st.metric(label="**Average HR**", value=f"{selected_avg_heartrate} BPM")
with col4:
    st.metric(label="**Average Cadence**", value=f"{selected_avg_cadence} SPM")


st.divider()

st.write('## Coach\'s Reccomendations')
st.markdown(':green[ ***Analysis of your current week\'s performance and future recommendations*** ]')

st.write(coach_reccomendation(runs, weekly_data))
st.divider()

# displaying table of runs
st.write('## All Run Statistics')
st.markdown(':green[ ***A table of all your runs you have logged. Click on headers to sort your data in different ways.*** ]')
st.dataframe(final, width=800)

# print(display_num_weeks)
# print(runs)
# print(final)
# print(weekly_mileage)

# response = gemini.generate_content('tell me a funny joke')
# print(response.text)

