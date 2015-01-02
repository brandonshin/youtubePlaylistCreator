#!/usr/bin/python

import httplib2
import os
import csv
import argparse
import os
import sys
import json
import requests as re
from apiclient.discovery import build
from apiclient.errors import HttpError
from oauth2client.client import flow_from_clientsecrets
from oauth2client.file import Storage
from oauth2client.tools import argparser, run_flow
DEVELOPER_KEY = "DEVELOPER KEY HERE"

# The CLIENT_SECRETS_FILE variable specifies the name of a file that contains
# the OAuth 2.0 information for this application, including its client_id and
# client_secret. You can acquire an OAuth 2.0 client ID and client secret from
# the Google Developers Console at
# https://console.developers.google.com/.
# Please ensure that you have enabled the YouTube Data API for your project.
# For more information about using OAuth2 to access the YouTube Data API, see:
#   https://developers.google.com/youtube/v3/guides/authentication
# For more information about the client_secrets.json file format, see:
#   https://developers.google.com/api-client-library/python/guide/aaa_client_secrets
CLIENT_SECRETS_FILE = "client2.json"

# This variable defines a message to display if the CLIENT_SECRETS_FILE is
# missing.
MISSING_CLIENT_SECRETS_MESSAGE = """
WARNING: Please configure OAuth 2.0

To make this sample run you will need to populate the client_secrets.json file
found at:

   %s

with information from the Developers Console
https://console.developers.google.com/

For more information about the client_secrets.json file format, please visit:
https://developers.google.com/api-client-library/python/guide/aaa_client_secrets
""" % os.path.abspath(os.path.join(os.path.dirname(__file__),
                                   CLIENT_SECRETS_FILE))

# This OAuth 2.0 access scope allows for full read/write access to the
# authenticated user's account.
YOUTUBE_READ_WRITE_SCOPE = "https://www.googleapis.com/auth/youtube"
YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"
YOUTUBE_REDIRECT_URI = "http://localhost:4000"
class Authenticator():
  def __init__(self):
    self.client_id = ''
    self.redirect_uri = ''
    self.scope = ''
    self.response_type = ''
    self.access_type = 'offline'
    self.client_secret = ''
    self.code = ''
  def createURL(self):
    self.readClientJSON("client2.json")
    url = "https://accounts.google.com/o/oauth2/auth?client_id=" + self.client_id +"&redirect_uri="+self.redirect_uri+"&scope="+self.scope+"&response_type="+self.response_type+"&access_type="+self.access_type
    print url
    self.acceptedConfirmation()
  def readClientJSON(self, x):
    with open(x) as json_file:
      json_data = json.load(json_file)
    self.client_id = json_data['web']['client_id']
    self.redirect_uri = json_data['web']['redirect_uris'][0]
    self.client_secret = json_data['web']['client_secret']
    print self.client_secret
    self.scope = "https://www.googleapis.com/auth/youtube"
    self.response_type = 'code'
    self.access_type = 'offline'
  def useCode(self):
    self.grant_type = "authorization_code"
    posts = {'code': self.code,
    'client_id': self.client_id,
    'client_secret': self.client_secret,
    'redirect_uri': self.redirect_uri,
    'grant_type': self.grant_type}
    sessions = re.session()
    print posts
    r = re.post("https://accounts.google.com/o/oauth2/token", data=posts)
    print r.text
    jsonFile = r.json()
    with open('access.json', 'w') as outfile:
      json.dump(jsonFile, outfile)
  def acceptedConfirmation(self):
    accepted = 'n'
    while accepted.lower() == 'n':
      accepted = raw_input("Have you authorized me? (y/n)")
    self.code = raw_input("What is the code?")
    self.useCode()
def get_authenticated_service():
  flow = flow_from_clientsecrets(CLIENT_SECRETS_FILE,
    message=MISSING_CLIENT_SECRETS_MESSAGE,
    scope=YOUTUBE_READ_WRITE_SCOPE,
    redirect_uri = YOUTUBE_REDIRECT_URI)


  storage = Storage("%s-oauth2.json" % sys.argv[0])
  credentials = storage.get()

  if credentials is None or credentials.invalid:
    flags = argparser.parse_args()
    credentials = run_flow(flow, storage, flags)

  return build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION,
    http=credentials.authorize(httplib2.Http()))
def createPlaylist(youtube):
  # This code creates a new, private playlist in the authorized user's channel.
  playlists_insert_response = youtube.playlists().insert(
    part="snippet,status",
    body=dict(
      snippet=dict(
        title="Test Playlist",
        description="A private playlist created with the YouTube API v3"
      ),
      status=dict(
        privacyStatus="private"
      )
    )
  ).execute()

  print "New playlist id: %s" % playlists_insert_response["id"]
  playlistID = playlists_insert_response["id"]
  return playlistID
class NewArgument():
  def __init__(self):
    pass

  def createQuery(self, songInfo):
    parser = argparse.ArgumentParser()
    parser.add_argument("--q", help="Search term", default=songInfo)
    parser.add_argument("--max-results", help="Max results", default=1)
    args = parser.parse_args()
    return args
class VideoStore():
  def __init__(self):
    self.videosArray = []
  def out(self):
    return self.videosArray
def youtube_search(options):
  youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION,
    developerKey=DEVELOPER_KEY)

  # Call the search.list method to retrieve results matching the specified
  # query term.
  search_response = youtube.search().list(
    q=options.q,
    part="id,snippet",
    maxResults=options.max_results
  ).execute()

  videos = []

  # Add each result to the appropriate list, and then display the lists of
  # matching videos, channels, and playlists.
  for search_result in search_response.get("items", []):
    if search_result["id"]["kind"] == "youtube#video":
      # videos.append("%s (%s)" % (search_result["snippet"]["title"],
      #                            search_result["id"]["videoId"]))
      videos.append("%s" % (search_result["id"]["videoId"]))
      print "%s" % (search_result["snippet"]["title"])
  return videos
def add_video_to_playlist(youtube,videoID,playlistID):
  add_video_request=youtube.playlistItems().insert(
  part="snippet",
  body={
        'snippet': {
          'playlistId': playlistID, 
          'resourceId': {
                  'kind': 'youtube#video',
              'videoId': videoID
            }
        #'position': 0
        }
  }
  ).execute()
def parseSongList(fileName):
  input = open(fileName, 'rU')
  data = csv.reader(input)
  data = list(data)
  return data

if __name__ == "__main__":
  data = parseSongList('pitchforkpoll.txt')
  youtube = get_authenticated_service()
  videoStore = VideoStore()
  playListID = createPlaylist(youtube)
  for row in data:
      songInfo  = row[0]
      argument = NewArgument()
      argument = argument.createQuery(songInfo.decode('utf-8'))
      try:
        video = youtube_search(argument)
        try:
          add_video_to_playlist(youtube,video[0],playListID)
        except IndexError:
          pass
      except UnicodeDecodeError:
        pass
      except HttpError, e:
        print "An HTTP error %d occurred:\n%s" % (e.resp.status, e.content)
  print videoStore.videosArray

