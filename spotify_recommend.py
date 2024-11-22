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


    def get_recommendations(self,song_title):
        # 노래 검색
        results = self.sp.search(q=song_title, type='track', limit=1)
        
        if not results['tracks']['items']:
            print("No track found with that name.")
            return
        
        track = results['tracks']['items'][0]
        print(f"Found track: {track['name']} by {track['artists'][0]['name']}")

        # 추천 곡 받기
        # 트랙 ID를 기반으로 추천을 요청
        recommendations = self.sp.recommendations(seed_tracks=[track['id']], limit=10)
        
        print(f"\nRecommended songs based on '{track['name']}':\n")
        
        for idx, rec in enumerate(recommendations['tracks'], 1):
            print(f"{idx}. {rec['name']} by {', '.join(artist['name'] for artist in rec['artists'])}")
            print(f"  Spotify URL: {rec['external_urls']['spotify']}")
            print()

if __name__ == '__main__':
    # 사용자로부터 노래 제목 입력받기
    spotipy_client = SpotifyClient()
    song_title = input("Enter song title: ")
    spotipy_client.get_recommendations(song_title)
