import pandas as pd
from dotenv import load_dotenv
import google.generativeai as genai
import os
import streamlit as st

load_dotenv()
genai.configure(api_key=os.environ["GOOGLE_API_KEY"]) # Configure the API key
gemini = genai.GenerativeModel('gemini-pro') # Create a Gemini Pro model

# function to process metric
def process_metric(metric_value):
    if pd.isna(metric_value):
        return 0 
    return round(metric_value)

# function to query gemini AI for analysis of runs comparing current week and previous week
@st.cache_data
def coach_reccomendation(runs, prev_week, current_week):
    # AI Recommendation 
    prev_week_df = runs[runs['start_week'] == prev_week]
    prev_total_distance = round(prev_week_df['distance'].sum(), 2)
    prev_num_runs = len(prev_week_df)
    prev_avg_heartrate = prev_week_df['average_heartrate'].mean()
    prev_avg_cadence = prev_week_df['average_cadence'].mean()

    current_week_df = runs[runs['start_week'] == current_week]
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
    Have a positive and encouraging tone. Include the data provided in your response but keep it relatively concise. Including a table
    of data where necessary would be useful.
    """
    response = gemini.generate_content(query)
    return response.text