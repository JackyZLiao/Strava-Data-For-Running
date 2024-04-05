import pandas as pd
from pandas import json_normalize
import requests
import json
import time


def retrieve_run_data():
    # get tokens from file to connect to Strava
    with open('stravaTokens.json') as file:
        stravaTokens = json.load(file)

    # if access token as expired then use the refreshToken to get new access token 
    if stravaTokens['expires_at'] < time.time():
        response = requests.post(
        url = 'https://www.strava.com/oauth/token',
        data = {
            'client_id': 121798,
            'client_secret': '90a6bd7310306ac7f85bbbd1ee137097e0097e74',
            'code': '3e616f83b131c6b13f0010da7d7a4f24402d97e4',
            'grant_type': 'refresh_token',
            'refresh_token': stravaTokens['refresh_token']
            }
        )

        # save response as json in new variable
        newStravaTokens = response.json()

        # save new tokens to file 
        with open('stravaTokens.json', 'w') as file:
            json.dump(newStravaTokens, file)

        # use new Strava tokens from now 
        stravaTokens = newStravaTokens

    # Loop through all activities 
    page = 1
    url = "https://www.strava.com/api/v3/activities"
    accessToken = stravaTokens['access_token']

    while True:
        # get page of activities from Strava
        r = requests.get(url + '?access_token=' + accessToken + '&per_page=200' + '&page=' + str(page))
        r = r.json()
        # if no results then exit loop
        if (not r):
            break
        data = json_normalize(r)
        data.to_csv('runData.csv')
        page += 1

