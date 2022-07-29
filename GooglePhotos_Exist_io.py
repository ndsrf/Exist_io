# This file requires some packages to be installed using pip
# See this:
# https://github.com/polzerdo55862/google-photos-api/blob/27a0ec0d99e0acfc101c2b31dbc6cd967c27e5d6/Google_API.ipynb

#  We store the info in the facebook_posts attribute in exist.io

import pickle
import os
from google_auth_oauthlib.flow import Flow, InstalledAppFlow
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
import requests
import json
import pandas as pd
from datetime import date

MY_TIMEZONE = "Europe/Madrid" # convert google photos timestamp to local time

# exist.io details
PAGINA_MAX = 35 # max days to update at once per post for the exist.io api
BEARER_TOKEN = '1111 BEARER TOKEN 1111' # bearer token for exist.io

## FROM THIS DATE - TO TODAY WILL BE UPDATED
RETRIEVE_PHOTOS_FROM_YEAR = 2022 
RETRIEVE_PHOTOS_FROM_MONTH = 7
RETRIEVE_PHOTOS_FROM_DAY = 26

# This script will run some authentication on first run and will save the credentials to a pickle file
# details below (see GooglePhotosApi function)
# Google auth code copied from https://github.com/polzerdo55862/google-photos-api/blob/27a0ec0d99e0acfc101c2b31dbc6cd967c27e5d6/Google_API.ipynb



#    payload = {
#                  "pageToken": pagetoken,
#                  "pageSize": 100,
#                  "filters": {
#                    "dateFilter": {
#                      "dates": [
#                        {
#                          "month": month,
#                          "year": year,
#                          "day" : day,
#                        }
#                      ]
#                    }
#                  }
#                }


def get_response_from_medium_api(year, month, day, pagetoken):
    url = 'https://photoslibrary.googleapis.com/v1/mediaItems:search'
    payload = {
                  "pageToken": pagetoken,
                  "pageSize": 100,
                  "filters": {
                    "dateFilter": {
                      "ranges": [
                        { "startDate": 
                            {
                            "year": year,
                            "month": month,
                            "day" : day,
                            },
                          "endDate": 
                            {
                            "year": date.today().year,
                            "month": date.today().month,
                            "day" : date.today().day,
                            }
                        }
                      ]
                    }
                  }
                }
    headers = {
        'content-type': 'application/json',
        'Authorization': 'Bearer {}'.format(creds.token)
    }
    
    try:
        res = requests.request("POST", url, data=json.dumps(payload), headers=headers)
    except:
        print('Request error') 
    
    return(res)


class GooglePhotosApi:
    def __init__(self,
                 api_name = 'photoslibrary',
                 client_secret_file= r'./credentials.json',
                 api_version = 'v1',
                 scopes = ['https://www.googleapis.com/auth/photoslibrary']):
        '''
        Args:
            client_secret_file: string, location where the requested credentials are saved
            api_version: string, the version of the service
            api_name: string, name of the api e.g."docs","photoslibrary",...
            api_version: version of the api
        '''

        self.api_name = api_name
        self.client_secret_file = client_secret_file
        self.api_version = api_version
        self.scopes = scopes
        self.cred_pickle_file = f'./GooglePhotos_Exist_io_{self.api_name}_{self.api_version}.pickle'

        self.cred = None

    def run_local_server(self):
        # is checking if there is already a pickle file with relevant credentials
        if os.path.exists(self.cred_pickle_file):
            with open(self.cred_pickle_file, 'rb') as token:
                self.cred = pickle.load(token)

        # if there is no pickle file with stored credentials, create one using google_auth_oauthlib.flow
        if not self.cred or not self.cred.valid:
            if self.cred and self.cred.expired and self.cred.refresh_token:
                self.cred.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(self.client_secret_file, self.scopes)
                self.cred = flow.run_local_server()

            with open(self.cred_pickle_file, 'wb') as token:
                pickle.dump(self.cred, token)
        
        return self.cred

# initialize photos api and create service
google_photos_api = GooglePhotosApi()
creds = google_photos_api.run_local_server()

nextPageToken = ""

dicc = {}

try:

  while True:
    response = get_response_from_medium_api(RETRIEVE_PHOTOS_FROM_YEAR, RETRIEVE_PHOTOS_FROM_MONTH, RETRIEVE_PHOTOS_FROM_DAY, nextPageToken)
    responsejson = response.json()
    if 'nextPageToken' in responsejson:
      nextPageToken = responsejson['nextPageToken']
    else:
      nextPageToken = ""

    for item in responsejson['mediaItems']:
      ts = pd.Timestamp(item['mediaMetadata']['creationTime']).tz_convert(MY_TIMEZONE)
      clave = ts.strftime('%Y-%m-%d')
      if clave in dicc:
        dicc[clave] = dicc[clave] + 1
      else:
        dicc[clave] = 1

    if nextPageToken == "":
      break

except:
    print(response.text)


# BEFORE calling exist.io you must
# 0. Create client https://exist.io/account/apps/
# 1. authorise, by opening in chrome the following URL 
# https://exist.io/oauth2/authorize?response_type=code&client_id=xxxxx&redirect_uri=https://localhost/&scope=read+write
# 2. Get bearer token
# 3. Activate facebook_posts attribute
#url = 'https://exist.io/api/1/attributes/acquire/'
#attributes = [{"name":"facebook_posts", "active":True}]
#response = requests.post(url, headers={'Authorization':'Bearer 58bearertoken27272', 'Content-Type': 'application/json; charset=utf-8'},data=json.dumps(attributes))



attributes = []
i = 0
url = 'https://exist.io/api/1/attributes/update/'

for x in dicc:
  attributes.append({"name": "facebook_posts", "date": x, "value": dicc[x]})
  i=i+1
  if i==PAGINA_MAX:
      data = json.dumps(attributes)
      response = requests.post(url, headers={'Authorization':f'Bearer {BEARER_TOKEN}', 'Content-Type': 'application/json; charset=utf-8'}, data=data)
      print("RESET")
      i=0
      attributes = []

if len(attributes)>0:
    data = json.dumps(attributes)
    response = requests.post(url, headers={'Authorization':f'Bearer {BEARER_TOKEN}', 'Content-Type': 'application/json; charset=utf-8'}, data=data)


print("Process completed")
