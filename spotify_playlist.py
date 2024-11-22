import spotipy
from spotipy.oauth2 import SpotifyOAuth
from dotenv import load_dotenv
import os
import csv
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

        # Spotipy initialization
        self.scope = "playlist-read-private playlist-read-collaborative"
        self.sp = spotipy.Spotify(
            auth_manager=SpotifyOAuth(
                client_id=client_id,
                client_secret=client_secret,
                redirect_uri=redirect_uri,
                scope=self.scope,
            )
        )

    def find_playlists_by_song(self,song_title):
        # 노래 검색
        results = self.sp.search(q=song_title, type='track', limit=10)
        
        if not results['tracks']['items']:
            print("No track found with that name.")
            return
        
        track = results['tracks']['items'][0]
        print(f"Found track: {track['name']} by {track['artists'][0]['name']}")

        # 해당 트랙을 포함한 플레이리스트 검색
        playlists = self.sp.search(q=track['name'], type='playlist', limit=5)
        
        if not playlists['playlists']['items']:
            print("No playlists found containing this song.")
            return
        
        print(f"Playlists containing '{track['name']}':")
        for idx, playlist in enumerate(playlists['playlists']['items'], 1):
            print(f"{idx}. {playlist['name']} - {playlist['external_urls']['spotify']}")

if __name__ == '__main__':
    spotipy_client = SpotifyClient()
    song_title = input("Enter song title: ")
    spotipy_client.find_playlists_by_song(song_title)
