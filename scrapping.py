# import tweepy
# import json
# # Your credentials
# with open('key.json') as config_file:
#     config = json.load(config_file)

# API_KEY = config['TW_API_KEY']
# API_SECRET = config['TW_API_SECRET']
# ACCESS_TOKEN = config['ACCESS_TOKEN']
# ACCESS_TOKEN_SECRET = config['ACCESS_TOKEN_SECRET']

# # Authenticate to the API
# auth = tweepy.OAuthHandler(API_KEY, API_SECRET)
# auth.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
# api = tweepy.API(auth)

# # Fetch the latest tweet from a user (e.g., Fabrizio Romano)
# tweets = api.user_timeline(screen_name='FabrizioRomano', count=1)

# for tweet in tweets:
#     print(tweet.full_text)
import requests

url = "https://api-football-beta.p.rapidapi.com/fixtures/statistics"

querystring = {"fixture":"37899"}

headers = {
	"X-RapidAPI-Key": "663502f1dcmshef755013c82c60cp15a6fejsn350986ce6b02",
	"X-RapidAPI-Host": "api-football-beta.p.rapidapi.com"
}

response = requests.get(url, headers=headers, params=querystring)

print(response.json())

# Check if the request was successful and process the data

# if response.status_code == 200:

#     # Convert the JSON response to a PySpark DataFrame

#     json_data = response.json()

    

#     # Extract 'response' part from the API data

#     response_data = json_data.get('response', [])
