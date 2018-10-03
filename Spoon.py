# -*- coding: utf-8 -*-
import os
import flask
import requests
import json

from Colors import Colors
import google.oauth2.credentials
import google_auth_oauthlib.flow
import googleapiclient.discovery
from googleapiclient.errors import HttpError
from datetime import datetime

API_SERVICE_NAME = 'youtube'
API_VERSION = 'v3'

CRED_FILE = json.loads(open(os.path.dirname(__file__) + '/credentials.json', "rt").read())
SETTINGS = json.loads(open(os.path.dirname(__file__) + '/settings.json', "rt").read())

credentials = google.oauth2.credentials.Credentials(**CRED_FILE)
youtube = googleapiclient.discovery.build(API_SERVICE_NAME, API_VERSION, credentials=credentials)

def main():
    print(Colors.HEADER + Colors.UNDERLINE + Colors.OKGREEN + "Music Spoon Commence!" + Colors.ENDC)
    print(Colors.BOLD + Colors.OKBLUE +"Last Import: %s" % SETTINGS['lastImport'])
    ids = get_upload_playlist_ids()
    video_ids = get_playlist_item_ids(ids)

    count = add_videos_to_watch_later(video_ids)

    update_settings()
    save_new_credentials(credentials)

    print("Added %s Videos" % str(count))

def get_upload_playlist_ids():
    print(Colors.BOLD + Colors.OKGREEN + "Start Getting Playlist" + Colors.ENDC)
    channels_to_get = ['UC3ifTl5zKiCAhHIBQYcaTeg',"UCwIgPuUJXuf2nY-nKsEvLOg","UCalCDSmZAYD73tqVZ4l8yJg","UCXKr4vbqJkg4cXmdvaAEjYw","UCXIyz409s7bNWVcM-vjfdVA","UCp0gATorETNZ6ttOTMeV7jA","UCQ5DkUL8c_vbflfQ8LRsCIg","UC5nc_ZtjKW1htCVZVRxlQAQ","UC65afEgL62PGFWXY7n6CUbA","UCSa8IUd1uEjlREMa21I3ZPQ","UCxH0sQJKG6Aq9-vFIPnDZ2A","UCmDM6zuSTROOnZnjlt2RJGQ","UCpDJl2EmP7Oh90Vylx0dZtA","UC8QfB1wbfrNwNFHQxfyNJsw","UCoK6vfCS2R9Qo6KEjb7niYA","UChVfER-3s533FTh8Uae0Rhg","UCqhNRDQE_fqBDBwsvmT8cTg","UC4rasfm9J-X4jNl9SvXp8xA","UC9UTBXS_XpBCUIcOG7fwM8A","UCEdvpU2pFRCVqU6yIPyTpMQ","UCC7ElkFVK3m03gEMfaq6Ung","UCBYg9_11ErMsFFNR66TRuLA","UCxnS0WDBVfBnTP2e97DYDSA","UCGwALZJISywbMsd3QPvvrDQ","UCEi0EgWJ5m7gVBQ68a1L0TA","UCVoraDictyd89xgZt-J2Frw","UCDE5Ezmxq1bNVak4lmkpCMw","UClVrJwcIy7saPcGc1nct80A","UCToUNe4i9j_SlKGFl8MrQHg","UCJ6td3C9QlPO9O_J5dF4ZzA","UCH-T4tFvtcPkbI4sCi237BA","UCtuFxawHK5fDrA8yFy8Vo1Q","UCPRvJpnEZFonePU9fJGcLLQ","UCq3Ci-h945sbEYXpVlw7rJg","UCAuFghi1ubOPTjvghHn-9Ow","UCiwQVBsNcoNdchvRqGxcYEA","UCU27SVe_x0TF8kyVDndguvg","UCD3Bhskiu9XXLTtPK97AhBA","UCApnql05Ym89GCXAyv0WZxA","UCxbAkvt-BhR44hlgD8d8WxQ","UCoQJcz3rOY-CbzM-t4CRioQ","UCnW6K9iOXQ6VJVisrlnQ3VA","UCuCLcV6b6YcWtzqv7QRdmKQ","UCGp8q-bv5-LxOJuIRlyH3_Q","UC2zRkMYVJycWecfmDkY2ynA","UCLTZddgA_La9H4Ngg99t_QQ","UC_LfW1R3B0of9qOw1uI-QNQ","UCar5SrXLuUKFfUcQXwkdbWg","UCBVjMGOIkavEAhyqpxJ73Dw","UCU4qlPNKbtQxH3KEiy4_aIA"]
    upload_ids = []
    channels_this_batch = ""

    for x, channel_id in enumerate(channels_to_get):
        channels_this_batch += channel_id + ','

        if x % 5 == 0:
            channels_this_batch[:-1]
            # print(channels_this_batch)

            channels = youtube.channels().list(id=channels_this_batch, part='contentDetails,snippet').execute()
            
            for channel in channels['items']:
                print(Colors.CYAN + " - Getting %s Playlist ID" % channel['snippet']['title'])
                upload_ids.append(channel['contentDetails']['relatedPlaylists']['uploads'])

            channels_this_batch = ""

    return upload_ids

def get_playlist_item_ids(upload_ids):
    print(Colors.BOLD + Colors.OKGREEN + "Getting Video IDs From Playlists")
    video_ids = []

    def loop_to_get_video_ids(playlist_items):
        for video in playlist_items:
            videoId = video['contentDetails']['videoId']
            published_on = datetime.strptime(video['contentDetails']['videoPublishedAt'], "%Y-%m-%dT%H:%M:%S.%fZ")

            if published_on > datetime.strptime(SETTINGS['lastImport'], "%Y-%m-%d"):
                video_ids.append(videoId)

    for pl_id in upload_ids:
        print(Colors.CYAN + " - Getting Playlist %s" % pl_id)
        playlist_request = youtube.playlistItems().list(playlistId=pl_id, part='contentDetails')
        playlist = playlist_request.execute()
    
        loop_to_get_video_ids(playlist['items'])

        for next_page in range(2):
            playlist_request = youtube.playlistItems().list_next(previous_request=playlist_request, previous_response=playlist)

            if playlist_request is not None:
                playlist = playlist_request.execute()
                loop_to_get_video_ids(playlist['items'])

    return video_ids

def add_videos_to_watch_later(video_ids):
    print(Colors.BOLD + Colors.OKGREEN + "Add Videos to Watch Later" + Colors.ENDC)
    count = 0

    for video_id in video_ids:
        print(Colors.CYAN + "Video %s being Added" % video_id)
        body = {
            "snippet": {
                "playlistId": "WL",
                "resourceId": {
                    "kind": "youtube#video",
                    "videoId": video_id
                }
            }
        }
        try:
            add_to_watch_later_request = youtube.playlistItems().insert(body=body, part="snippet")
            add_to_watch_later_response = add_to_watch_later_request.execute()
            count +=1
        except HttpError:
            print(Colors.FAIL + " - %s Already Added?" % video_id)

    return count

def update_settings():
    print(Colors.BOLD + Colors.OKGREEN + "Updating Settings" + Colors.ENDC)
    today = datetime.today().strftime("%Y-%m-%d")
    
    SETTINGS['lastImport'] = today.__str__()

    open(os.path.dirname(__file__) + '/settings.json', "w").write(json.dumps(SETTINGS))

def credentials_to_dict(credentials):
  return {'token': credentials.token,
          'refresh_token': credentials.refresh_token,
          'token_uri': credentials.token_uri,
          'client_id': credentials.client_id,
          'client_secret': credentials.client_secret,
          'scopes': credentials.scopes}

def save_new_credentials(credentials):
    print(Colors.BOLD + Colors.OKGREEN + "Updating Credentials" + Colors.ENDC)
    new_json = json.dumps(credentials_to_dict(credentials))
    open(os.path.dirname(__file__) + '/credentials.json', "w").write(new_json)


if __name__ == '__main__':
    main()