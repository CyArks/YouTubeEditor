import googleapiclient.errors
import httplib2
import os
import sys
import pandas as pd
# import openpyxl

from googleapiclient.discovery import build
from oauth2client.client import flow_from_clientsecrets
from oauth2client.file import Storage
from oauth2client.tools import run_flow
from pprint import pprint

# The CLIENT_SECRETS_FILE variable specifies the name of a file that contains
# the OAuth 2.0 information for this application, including its client_id and
# client_secret. You can acquire an OAuth 2.0 client ID and client secret from
# the Google Cloud Console at
# https://cloud.google.com/console.

CLIENT_SECRETS_FILE = "client_secrets.json"

MISSING_CLIENT_SECRETS_MESSAGE = """
   WARNING: Please configure OAuth 2.0

   To make this sample run you will need to populate the client_secrets.json file
   found at:

   %s

   with information from the Cloud Console
   https://cloud.google.com/console

   For more information about the client_secrets.json file format, please visit:
   https://developers.google.com/api-client-library/python/guide/aaa_client_secrets
   """ % os.path.abspath(os.path.join(os.path.dirname(__file__),
                                      CLIENT_SECRETS_FILE))

YOUTUBE_SCOPE = "https://www.googleapis.com/auth/youtube"
YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"
targetPlaylist = "PLei_nvJru1BDHPa1HL92eRlX_A7alc5Ci"
videoURL = "noMjvKG3ovQ"

def get_authenticated_service():
    flow = flow_from_clientsecrets(CLIENT_SECRETS_FILE, scope=YOUTUBE_SCOPE,
                                   message=MISSING_CLIENT_SECRETS_MESSAGE)

    storage = Storage("%s-oauth2.json" % sys.argv[0])
    credentials = storage.get()

    if credentials is None or credentials.invalid:
        credentials = run_flow(flow, storage)

    return build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION,
                 http=credentials.authorize(httplib2.Http()))


class Search:
    def __init__(self):
        self.youtube = get_authenticated_service()

    def search(self, searchKey: str):   # search by Keyword
        response = self.youtube.search().list(
            part="snippet",
            maxResults=50,
            q=searchKey
        )
        return response.execute()


class Video:
    def __init__(self, videoID):
        self.id = videoID

        self.title = None
        self.length = None
        self.artist = None

    def getLength(self):
        pass

    def getTitle(self):
        pass

    def getPopularVideos(self):
        pass


class Playlist:
    def __init__(self, PlaylistID=None):
        self.id = PlaylistID
        self.youtube = get_authenticated_service()

        self.title = None
        self.playlistElements = None
        self.playlistLength = None

    def AddItem(self, videoID: str):
        try:
            add_video_request = self.youtube.playlistItems().insert(
                part="snippet",
                body={
                    'snippet': {
                        'playlistId': self.id,
                        'resourceId': {
                            'kind': 'youtube#video',
                            'videoId': videoID
                        }
                        # 'position': 0
                    }
                }
            )
            add_video_request.execute()
        except googleapiclient.errors.HttpError as e:
            print("Playlist not found \n ", e)

    def getTitle(self):
        response = self.youtube.playlists().list(
            part="snippet",
            id=self.id
        ).execute()

        title = response.get('items')[0]['snippet'].get('localized').get('title')
        return title

    def editName(self):
        pass

    def delete(self):
        self.youtube.playlists().delete().execute()

    def getPlaylistVideos(self):
        try:
            maxResults = 50
            items = []

            response = self.youtube.playlistItems().list(
                part='contentDetails,snippet',
                playlistId=self.id,
                maxResults=maxResults
            ).execute()

            items.extend(response.get('items'))
            nextPageToken = response.get('nextPageToken')

            while nextPageToken:
                response = self.youtube.playlistItems().list(
                    part='contentDetails,snippet',
                    playlistId=self.id,
                    maxResults=maxResults,
                    pageToken=nextPageToken
                ).execute()
                items.extend(response.get('items'))
                nextPageToken = response.get('nextPageToken')
            return items

        except Exception as e:
            print(e)
            return

    def getLength(self):
        pass

    def getStatus(self):  # public / private / link-shared
        pass

    def create(self, title: str, status: str, description="", tags=None):
        request = self.youtube.playlists().insert(
            part="snippet,status",
            body={
                "snippet": {
                    "title": title,
                    "description": description,
                    "tags": [
                        tags
                    ],
                    "defaultLanguage": "en"
                },
                "status": {
                    "privacyStatus": status
                }
            }
        )
        return request.execute()
        # self.id = createdID

    def listItems(self):
        try:
            items = []
            response = self.youtube.playlists().list(
                part="snippet,contentDetails",
                maxResults=25,
                mine=True).execute()
            items.extend(response.get('items'))
            nextPageToken = response.get('nextPageToken')

            while nextPageToken:
                response = self.youtube.playlists().list(
                    part="snippet,contentDetails",
                    maxResults=25,
                    mine=True).execute()
                items.extend(response.get('items'))
                nextPageToken = response.get('nextPageToken')
            return items
        except Exception as err:
            print(err)
            return

    def listMine(self):
        try:
            items = []
            response = self.youtube.playlists().list(
                part="snippet,contentDetails",
                maxResults=250,
                mine=True
            ).execute()
            items.extend(response.get('items'))
            nextPageToken = response.get('nextPageToken')

            while nextPageToken:
                response = self.youtube.playlists().list(
                    part="snippet,contentDetails",
                    maxResults=250,
                    mine=True
                ).execute()
                items.extend(response.get('items'))
                nextPageToken = response.get('nextPageToken')
            return items
        except Exception as err:
            print(err)
            return

    def listAllPlaylistsForChannel(self, channelID: str):
        try:
            items = []
            response = self.youtube.playlists().list(
                part="snippet,contentDetails",
                channelId=channelID,
                maxResults=25
            ).execute()
            items.extend(response.get('items'))
            nextPageToken = response.get('nextPageToken')

            while nextPageToken:
                response = self.youtube.playlists().list(
                    part="snippet,contentDetails",
                    channelId=channelID,
                    maxResults=25,
                    nextPageToken=nextPageToken
                ).execute()
                items.extend(response.get('items'))
                nextPageToken = response.get('nextPageToken')
            return items
        except Exception as err:
            print(err)
            return

    def listMyLikes(self):
        request = self.youtube.videos().list(
            part="snippet,contentDetails,statistics",
            myRating="like",
            maxResults=300
        )
        return request.execute()

    def listMyDislikes(self):
        request = self.youtube.videos().list(
            part="snippet,contentDetails,statistics",
            maxResults=300,
            myRating="dislike"
        )
        return request.execute()

    def createBackup(self, items: list, backupPath=None):
        if backupPath is None:
            backupPath = f"{os.getcwd()}\\{self.getTitle()}_backup.xlsx"
        try:
            if not backupPath.endswith('.xlsx'):
                print("Warning! Invalid excel path, path hast to end with xlsx!")
                return

            xlWriter = pd.ExcelWriter(backupPath)
            df = pd.DataFrame(items)

            df['snippet'].apply(pd.Series).to_excel(xlWriter, sheet_name='snippet', index=False)
            df['contentDetails'].apply(pd.Series).to_excel(xlWriter, sheet_name='contentDetails', index=False)
            xlWriter.save()

            print(f'Export is saved at {backupPath}')
        except Exception as e:
            print(e)
            return


playlistIds = ['PLei_nvJru1BDnEvoYmigBWl25hnV5WhFH', "PLei_nvJru1BDNNgNIHeHtKTgUK7TO9uqy"]


for playlistId in playlistIds:
    p = Playlist(PlaylistID=playlistId)
    playlistItems = p.getPlaylistVideos()
    # if a playlist has no video, then there is nothing to export
    if playlistItems:
        p.createBackup(playlistItems)

se = Search().search("One Republic")
pprint(se)

# Pl = Playlist()
# pprint(Pl.listMine())
# pprint(Pl.listMyLikes())

# x = Pl.create("TestPlaylist", "private")
# print(x)
