# import requests
# import json

# # Make Strava auth API call with your client code, client secret and code 
# response = requests.post(
#     url = 'https://www.strava.com/oauth/token',
#     data = {
#         'client_id': 121798,
#         'client_secret': '90a6bd7310306ac7f85bbbd1ee137097e0097e74',
#         'code': '3e616f83b131c6b13f0010da7d7a4f24402d97e4',
#         'grant_type': 'authorization_code'
#     }
# )

# # save json response as a variable
# stravaToken = response.json()

# #save tokens to file 
# with open('stravaTokens.json', 'w') as outfile:
#     json.dump(stravaToken, outfile)

# # Open JSON file and print the file contents to check it has worked properly 
# with open('stravaTokens.json') as file:
#     data = json.load(file)
# print(data)