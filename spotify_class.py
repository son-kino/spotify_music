class SpotifyClient:
    def __init__(self):
        """ 환경 변수 가져오기 """
        client_id = os.getenv("CLIENT_ID")
        client_secret = os.getenv("CLIENT_SECRET")
        redirect_uri = os.getenv("REDIRECT_URI")

        # Spotipy 초기화
        self.scope = "playlist-read-private playlist-read-collaborative"
        self.sp = spotipy.Spotify(
            auth_manager=SpotifyOAuth(
                client_id=client_id,
                client_secret=client_secret,
                redirect_uri=redirect_uri,
                scope=self.scope,
            )
        )

    def get_recommendations(self, song_title):
        """ 추천곡을 가져오는 함수 """
        # 노래 검색
        results = self.sp.search(q=song_title, type='track', limit=1)
        
        if not results['tracks']['items']:
            print("No track found with that name.")
            return []
        
        track = results['tracks']['items'][0]
        print(f"Found track: {track['name']} by {track['artists'][0]['name']}")

        # 추천 곡 받기
        recommendations = self.sp.recommendations(seed_tracks=[track['id']], limit=10)
        
        recommendations_data = []
        for rec in recommendations['tracks']:
            album_cover_url = rec['album']['images'][0]['url']
            song_info = {
                "title": rec['name'],
                "link": rec['external_urls']['spotify'],
                "cover_image": album_cover_url
            }
            recommendations_data.append(song_info)

        return recommendations_data

    def find_playlists_by_song(self, song_title):
        """ 노래 제목을 입력받아 해당 노래가 포함된 플레이리스트를 찾는 함수 """
        # 노래 검색
        results = self.sp.search(q=song_title, type='track', limit=10)
        
        if not results['tracks']['items']:
            print("No track found with that name.")
            return []
        
        track = results['tracks']['items'][0]
        print(f"Found track: {track['name']} by {track['artists'][0]['name']}")

        # 해당 트랙을 포함한 플레이리스트 검색
        playlists = self.sp.search(q=track['name'], type='playlist', limit=5)
        
        if not playlists['playlists']['items']:
            print("No playlists found containing this song.")
            return []
        
        playlist_data = []
        for playlist in playlists['playlists']['items']:
            playlist_name = playlist['name']
            playlist_url = playlist['external_urls']['spotify']
            playlist_cover_url = playlist['images'][0]['url'] if playlist['images'] else 'No image available'
            playlist_info = {
                "title": playlist_name,
                "link": playlist_url,
                "cover_image": playlist_cover_url
            }
            playlist_data.append(playlist_info)

        return playlist_data