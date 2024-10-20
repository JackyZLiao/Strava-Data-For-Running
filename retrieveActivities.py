import requests
from pandas import json_normalize
import json
import csv

# Get the tokens from file to connect to Strava
with open('stravaTokens.json') as file:
    stravaTokens = json.load(file)
# Loop through all activities
url = "https://www.strava.com/api/v3/activities"
accessToken = stravaTokens['access_token']
# Get first page of activities from Strava with all fields
r = requests.get(url + '?access_token=' + accessToken)
r = r.json()
    
df = json_normalize(r)
df.to_csv('strava_activities_all_fields.csv')