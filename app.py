import pandas as pd
import streamlit as st
import plotly.express as px
from datetime import datetime, timedelta
from retrieve_run_data import retrieve_run_data
from helpers import process_metric, coach_reccomendation

# Check if CSV has been updated
if 'csv_up_to_date' not in st.session_state:
    retrieve_run_data() # retrieve latest run data
    st.session_state.csv_up_to_date = True # Store the flag to indicate that CSV file has been updated in the session

# **************************************** Intro Heading ****************************************
st.set_page_config(page_title='PacePal')
st.title('PacePal 🏃')
st.markdown(':green[ ***An application to track your runs and get insight into your statistics using Strava data*** ]')
st.divider()

# **************************************** Weekly Kilometres Graph ****************************************
st.write('## Weekly kilometres')
st.markdown(':green[ ***A visualisation of your total weekly distance. Adjust the slider to change the number of weeks shown*** ]')

# Load data 
df = pd.read_csv('runData.csv') # loading csv into dataframe
runs = df[['name', 'distance', 'moving_time', 'start_date_local', 'average_cadence', 'average_heartrate']] # only getting distance, time and date of runs

# Data preprocessing: Calculating derived metrics and formatting columns for visualization and analysis
runs['start_date_local'] = pd.to_datetime(runs['start_date_local']) # turning date into datetime object
runs['stride_length'] = round(runs['distance'] / (runs['moving_time'] / 60 * runs['average_cadence'] * 2), 2)
runs['distance'] = round(runs['distance'] / 1000, 2)
runs['start_week'] = runs['start_date_local'].dt.to_period('W')
runs['start_week'] = pd.to_datetime(runs['start_week'].astype(str).str.split('/').str[0]).dt.strftime('Week of %b %d \'%y')
runs['time'] = (runs['moving_time'] // 60).astype(str).str.zfill(2) + ':' + (runs['moving_time'] % 60).astype(str).str.zfill(2)
runs['pace'] = (runs['moving_time'] / runs['distance'] // 60).astype(int).astype(str) + ':' + (round(runs['moving_time'] / runs['distance'] / 60 % 1 * 60)).astype(int).astype(str).str.zfill(2)
runs['start_date_local'] = runs['start_date_local'].dt.strftime('%d-%m-%Y')
runs['average_cadence'] = (runs['average_cadence'] * 2)

# Aggregating data into their weeks and doing more data pre-processing
weekly_stats = runs.groupby('start_week').agg({
    'distance': 'sum', 
    'average_heartrate': 'mean', 
    'moving_time': 'sum', 
    'average_cadence': 'mean'
})
column_renaming = {'distance': 'Distance', 'average_heartrate': 'Heart rate', 'moving_time': 'Time', 'average_cadence': 'Cadence'}
weekly_stats = weekly_stats.rename(columns=column_renaming)
weekly_stats['Time'] = weekly_stats['Time'] // 60 
weekly_stats['Cadence'] = weekly_stats['Cadence'].fillna(0).round()
weekly_stats['Heart rate'] = weekly_stats['Heart rate'].fillna(0).round()

# select box to choose which stat to display
stat_to_display = st.selectbox('To display', ('Distance', 'Time', 'Heart rate', 'Cadence'))
# slider for weeks in the year 
num_weeks = st.slider('Number of weeks:', min_value=5, max_value=52, value=5)

# Generate week dates starting from today and going backwards
week_dates = [(datetime.now() - timedelta(days=datetime.now().weekday()) - timedelta(weeks=i)).strftime('Week of %b %d \'%y') for i in range(num_weeks)][::-1]

# Create a dict with weeks and distances to be displayed in column graph
weekly_individual_stat = {'Week': [], 'Statistic': []}
for week_date in week_dates:
    # if week has recorded runs, get weekly stat, else 0 
    stat = weekly_stats.loc[week_date, stat_to_display] if week_date in weekly_stats.index.tolist() else 0
    weekly_individual_stat['Week'].append(week_date)
    weekly_individual_stat['Statistic'].append(stat)

# convert into dataframe
display = pd.DataFrame(weekly_individual_stat)

# map different graph colours to different statistics 
colour_mapping = {'Distance' : '87CEEB', 'Heart rate': 'FF9999', 'Time': 'BDFCC9', 'Cadence': 'D0ACEA'}

# Plotting weekly kilometres into a column graph and displaying it + customsing it
column_graph = px.bar(display, x='Week', y='Statistic', title='Weekly Run Metrics Summary', height=600, width=800)
column_graph.update_traces(hovertemplate='%{y}', marker_color=f'#{colour_mapping[stat_to_display]}') # customising hover text and column colour
column_graph.update_layout(title={'font': {'size': 24}}, xaxis={'title': {'text': 'Week', 'font': {'size': 18}}, 'tickfont': {'size': 14}}, yaxis={'title': {'text': f"{stat_to_display}", 'font': {'size': 18}}, 'tickfont': {'size': 14}})

# displaying column graph
st.plotly_chart(column_graph)
st.divider()

# **************************************** Weekly Run Statistics Section ****************************************
st.write('## Weekly Run Statistics')
st.markdown(':green[ ***A weekly overview of your runs. Select a week from the dropdown to preview that week\'s runs and stats.*** ]')
select_week = st.selectbox('Select a week:', options=week_dates) # dropdown menu to select a particular week

selected_week_distance = selected_week_time = selected_week_hr = selected_week_cadence = 0
# get statistics for selected week
if select_week in weekly_stats.index:
    selected_week_distance = round(weekly_stats.loc[select_week, 'Distance'], 2) 
    selected_week_time = weekly_stats.loc[select_week, 'Time']
    selected_week_hr = process_metric(weekly_stats.loc[select_week, 'Heart rate'])
    selected_week_cadence = process_metric(weekly_stats.loc[select_week, 'Cadence'])

# Getting stats from the previous week
selected_index = week_dates.index(select_week)
prior_week_distance = prior_week_time = prior_week_hr = prior_week_cadence = 0
prior_week = week_dates[selected_index - 1] if selected_index != 0 else None

if prior_week in weekly_stats.index:
    prior_week_distance = round(weekly_stats.loc[prior_week, 'Distance'], 2)
    prior_week_time = weekly_stats.loc[prior_week, 'Time']
    prior_week_hr = process_metric(weekly_stats.loc[prior_week, 'Heart rate'])
    prior_week_cadence = process_metric(weekly_stats.loc[prior_week, 'Cadence'])

# Getting difference of stats between selected week and week prior
distance_diff = f"{round(selected_week_distance - prior_week_distance, 2)} km"
time_diff = f"{selected_week_time - prior_week_time} mins" if prior_week_time is not None else None
hr_diff = f"{selected_week_hr - prior_week_hr} BPM" if prior_week_hr is not None else None
cadence_diff = f"{selected_week_cadence - prior_week_cadence} SPM" if prior_week_cadence is not None else None

# drop unnecessary columns
selected_week_df = runs[runs['start_week'] == select_week].drop(columns=['start_week', 'time'])
st.dataframe(selected_week_df, width=800)

# displaying weekly statistics
col1, col2, col3, col4 = st.columns(4)
col1.metric(label="**Total Distance**", value=f"{selected_week_distance} km", delta=distance_diff)
col2.metric(label="**Total time**", value=f"{selected_week_time} mins", delta=time_diff)
col3.metric(label="**Average HR**", value=f"{selected_week_hr} BPM", delta=hr_diff, delta_color="inverse")
col4.metric(label="**Average Cadence**", value=f"{selected_week_cadence} SPM", delta=cadence_diff)
st.divider()

# ********** Coach's Reccomendations section: using Google Gemini to provide analysis/recommendations **********
st.write('## Coach\'s Reccomendations')
st.markdown(':green[ ***AI Analysis of your current week\'sperformance compared to last week, and future recommendations*** ]')

# Get the current week and the previous week as input for gemini model
prev_week = week_dates[-2]
current_week = week_dates[-1]
st.write(coach_reccomendation(runs, prev_week, current_week))
st.divider()

# **************************************** All Run Stats Section ****************************************
all_runs = runs.drop(columns=['start_week', 'moving_time'])
st.write('## All Run Statistics')
st.markdown(':green[ ***A table of all your runs you have logged. Click on headers to sort your data in different ways.*** ]')
st.dataframe(all_runs, width=800)