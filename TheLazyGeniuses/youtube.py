import pip

import time
import os
import sys

try:
  import serial
except Exception as e:
  pip.main(['install', 'pyserial'])

import google.oauth2.credentials

import google_auth_oauthlib.flow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google_auth_oauthlib.flow import InstalledAppFlow

from json import JSONDecoder

# The CLIENT_SECRETS_FILE variable specifies the name of a file that contains
# the OAuth 2.0 information for this application, including its client_id and
# client_secret.
CLIENT_SECRETS_FILE = "client_secret.json"

# This OAuth 2.0 access scope allows for full read/write access to the
# authenticated user's account and requires requests to use an SSL connection.
SCOPES = ['https://www.googleapis.com/auth/youtube.force-ssl']
API_SERVICE_NAME = 'youtube'
API_VERSION = 'v3'

ARDUINO_USB_PORT = 'COM4'
MAX_VIEWERS = 0

def get_authenticated_service():
  flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRETS_FILE, SCOPES)
  credentials = flow.run_console()
  return build(API_SERVICE_NAME, API_VERSION, credentials = credentials)

if len(sys.argv) < 2:
  print("Usage: python youtube.py <livestream_id> [ARDUINO_USB_PORT]")
  sys.exit()

# When running locally, disable OAuthlib's HTTPs verification. When
# running in production *do not* leave this option enabled.
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
client = get_authenticated_service()


if len(sys.argv) < 3:
  ser = serial.Serial(ARDUINO_USB_PORT, 19200)
else:
  ser = serial.Serial(sys.argv[2], 19200)

while True:
  try:
    response = client.videos().list(part='liveStreamingDetails', id=sys.argv[1]).execute()
    details = response['items'][0]['liveStreamingDetails']
    try:
      if int(details['concurrentViewers']) <= MAX_VIEWERS:
        ser.write(b'1')
      else:
        ser.write(b'0')
    except Exception as no_viewers:
      ser.write(b'1')

    time.sleep(3)

  except Exception as e:
    print('Video either is not a livestream or has finished.')
    print(e)
    print(response)

    break

