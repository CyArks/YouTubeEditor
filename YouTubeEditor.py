import googleapiclient.errors
import httplib2
import os
import sys
import pandas as pd

from googleapiclient.discovery import build
from oauth2client.client import flow_from_clientsecrets
from oauth2client.file import Storage
from oauth2client.tools import run_flow

# https://cloud.google.com/console.

CLIENT_SECRETS_FILE = "client_secrets.json"

SCOPE = "https://www.googleapis.com/auth/youtube"
API_SERVICE_NAME = "youtube"
API_VERSION = "v3"

"""Authentication process"""
def get_authenticated_service():
    flow = flow_from_clientsecrets(CLIENT_SECRETS_FILE, scope=SCOPE)

    storage = Storage("%s-oauth2.json" % sys.argv[0])
    credentials = storage.get()

    if credentials is None or credentials.invalid:
        credentials = run_flow(flow, storage)

    return build(API_SERVICE_NAME, API_VERSION,
                 http=credentials.authorize(httplib2.Http()))


class Search:
    def __init__(self):
        self.youtube = get_authenticated_service()

    """Search by Keyword --> Returns JSON"""
    def search(self, searchKey: str):
        response = self.youtube.search().list(
            part="snippet",
            maxResults=50,
            q=searchKey
        )
        return response.execute()


# coming soon
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

    """Add a Video to Playlist"""
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
                            # 'position': 0
                        }
                    }
                }
            )
            add_video_request.execute()
        except googleapiclient.errors.HttpError as e:
            print("Playlist not found \n ", e)

    """Get Playlist Title"""
    def getTitle(self):
        response = self.youtube.playlists().list(
            part="snippet",
            id=self.id
        ).execute()

        title = response.get('items')[0]['snippet'].get('localized').get('title')
        return title

    # coming soon
    def editName(self):
        pass

    """Delete Playlist from YouTube"""
    def delete(self):
        self.youtube.playlists().delete().execute()

    """Returns Videos in a Playlist"""
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

    # coming soon
    def getLength(self):
        pass

    # coming soon
    def getStatus(self):  # public / private / link-shared
        pass

    """Create a new YouTube Playlist"""
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

    """List Items in a YouTube Playlist"""
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

    """List all YouTube Playlists from Auth. User"""
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

    """List all YouTube Playlists for a channel"""
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

    """List all Likes from Auth. User"""
    def listMyLikes(self):
        request = self.youtube.videos().list(
            part="snippet,contentDetails,statistics",
            myRating="like",
            maxResults=300
        )
        return request.execute()

    """List all Dislikes from Auth. User"""
    def listMyDislikes(self):
        request = self.youtube.videos().list(
            part="snippet,contentDetails,statistics",
            maxResults=300,
            myRating="dislike"
        )
        return request.execute()

    """Create Playlist Backup"""
    def createBackup(self, backupPath=None):
        if backupPath is None:
            backupPath = f"{os.getcwd()}\\{self.getTitle()}_backup.xlsx"
        try:
            xlWriter = pd.ExcelWriter(backupPath)
            data = self.getPlaylistVideos()
            df = pd.DataFrame(data)

            df['snippet'].apply(pd.Series).to_excel(xlWriter, sheet_name='snippet', index=False)
            df['contentDetails'].apply(pd.Series).to_excel(xlWriter, sheet_name='contentDetails', index=False)
            xlWriter.save()

            print(f'Backup saved at {backupPath}')
        except Exception as e:
            print(e)
            return
