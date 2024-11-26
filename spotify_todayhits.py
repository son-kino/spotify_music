import spotipy
from spotipy.oauth2 import SpotifyOAuth
from dotenv import load_dotenv
import os
import logging

# 로깅 설정
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

class SpotifyClient:
    def __init__(self):
        """ 환경 변수 가져오기 """
        load_dotenv()

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

    def get_top_10_tracks_from_playlist(self):
        # 'Global Top 50' 플레이리스트 ID
        global_top_50_playlist_id = '37i9dQZEVXbMDoHDwVN2tF'  # 이 ID는 Spotify Global Top 50 플레이리스트의 ID입니다.
        
        # 플레이리스트에서 트랙 가져오기
        results = self.sp.playlist_tracks(global_top_50_playlist_id, limit=10)

        if not results['items']:
            print("No tracks found in the playlist.")
            return

        top_songs = []
        for item in results['items']:
            track = item['track']  # 트랙 정보는 'track' 키 아래에 존재합니다.
            album_cover_url = track['album']['images'][0]['url'] if track['album']['images'] else 'No image available'
            song_info = {
                "title": track['name'],
                "link": track['external_urls']['spotify'],
                "cover_image": album_cover_url
            }
            top_songs.append(song_info)

        print(top_songs)

        return top_songs
            
if __name__ == '__main__':
    spotipy_client = SpotifyClient()
    # Global Top 50 플레이리스트에서 상위 10곡 가져오기
    spotipy_client.get_top_10_tracks_from_playlist()
