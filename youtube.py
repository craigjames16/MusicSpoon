def add_to_youtube_playlist(self,user,trackId):
        token = user.youtube_token

        if user.youtube_token_expires < timezone.now():
           na='na' # token = self.refresh_youtube_user_token(user)

        headers = {'Authorization':'Bearer '+token}

        youtube_tracks = YoutubeData.objects.filter(track_id=trackId)
        if youtube_tracks:
            if user.youtube_playlist_id:
                if user.youtube_token_expires > timezone.now():
                    # self.refresh_youtube_user_token(user)
                    na='nothin'

                add_track_url = 'https://www.googleapis.com/youtube/v3/playlistItems?part=snippet'
                r = requests.post(add_track_url,json={
                    "snippet":{
                        "playlistId": user.youtube_playlist_id,
                        "resourceId": {
                          "kind": "youtube#video",
                          "videoId": youtube_tracks[0].youtube_id
                        }
                    }
                }, headers=headers)
                playlist_response = json.loads(r.text)

                return {'YTRESPONSE': playlist_response, 'INFO': youtube_tracks[0].youtube_id}

def refresh_youtube_token(self):
        redirect_uri = self.server_add + '/connect/?source=youtube'
        
        r = requests.post('https://www.googleapis.com/oauth2/v4/token', data = {'refresh_token':code,'client_id':self.youtube_client_id, 'client_secret': self.youtube_client_secret, 'redirect_uri': redirect_uri,'grant_type':'authorization_code'})
        response_json = json.loads(r.text)

def get_channel_list(self, channel):
        r = requests.get('https://www.googleapis.com/youtube/v3/channels?part=contentDetails,snippet&id='+channel+'&key='+self.youtubeAPI+'')
        channel_json = json.loads(r.text)

        upload_playlist_id = channel_json['items'][0]['contentDetails']['relatedPlaylists']['uploads']
        self.channel_source = 'youtube'
        
        r = requests.get('https://www.googleapis.com/youtube/v3/playlistItems?part=snippet&playlistId='+upload_playlist_id+'&maxResults=20&key='+self.youtubeAPI+'')
        playlist_json = json.loads(r.text)

        for item in playlist_json['items']:
            track = {}
            track['youtube_id'] = item['snippet']['resourceId']['videoId']
            track['dateposted'] = item['snippet']['publishedAt']
            track['youtube_thumb'] = item['snippet']['thumbnails']['default']['url']
            track['channel'] = {}
            track['channel']['channel_id'] = channel_json['items'][0]['id']
            track['channel']['channel_name'] = channel_json['items'][0]['snippet']['title']
            track['channel']['channel_thumb'] = channel_json['items'][0]['snippet']['thumbnails']['default']['url']
            track['channel']['channel_user'] = 'NA'

            artist_title = self.extract_artist_title(item['snippet']['title'])
            if artist_title:
                track['title'] = artist_title['title']
                track['artist'] = artist_title['artist']

                track = self.get_views_likes(track)
                
                track['match'] = {}
                self.track_list.append(track)                

        # return self.track_list