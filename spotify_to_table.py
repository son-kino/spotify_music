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


    def get_user_playlists(self):
        """사용자의 스포티파이 플레이리스트 가져오기"""
        # 이 부분은 추후 사용자가 넣은 플레이리스트트로 수정하거나 제거할 필요 있음
        print("\nUser Playlists:")
        playlists = self.sp.current_user_playlists()
        user_playlists = []
        while playlists:
            for playlist in playlists['items']:
                print(f"Name: {playlist['name']}, ID: {playlist['id']}")
                if playlist['name']:
                    user_playlists.append([playlist['name'],playlist['id']])
            playlists = self.sp.next(playlists) if playlists['next'] else None
        return user_playlists
    
    
    def get_featured_playlists(self):
        """전 세계적이거나 지역적으로 인기 있는 플레이리스트, 특정 계절 또는 테마에 맞춘 플레이리스트 가져오기"""
        print("\nFeatured Playlists:")
        playlists = self.sp.featured_playlists()
        featured_playlists = []
        for playlist in playlists['playlists']['items']:
            print(f"Name: {playlist['name']}, ID: {playlist['id']}")
            if playlist['name']:
                featured_playlists.append([playlist['name'],playlist['id']])
        return featured_playlists
    
    def list_categories(self):
        """키테고리 리스트 만들기"""
        print("\nAvailable Categories:")
        categories = self.sp.categories()
        categories_list= []
        for category in categories['categories']['items']:
            categories_list.append([category['name'],category['id']])
        return categories_list
    
    def get_category_playlists(self):
        """catrgoy_id list 가져와서 카테고리 플레이리스트 가져오기"""
        categories_list = self.list_categories()
        categories_playlists = {}
        
        for category_name,category_id in categories_list: #카테고리 아이디에서 플레이리스트 뽑아오기
            print(f"\nPlaylists for Category {category_name}:")
            category_playlist = []
            playlists = self.sp.category_playlists(category_id=category_id)
            
            for playlist in playlists['playlists']['items']: # 뽑아온 플레이리스트에서 아이템 가져오기
                print(playlist)
                print(f"Name: {playlist['name']}, ID: {playlist['id']}")
                if playlist['name']:
                    category_playlist.append([playlist['name'], playlist['id']])
            categories_playlists[category_name] = category_playlist
        return categories_playlists
    
    def validate_playlist(self, playlist_id):
        """플레이리스트 ID 유효성 검사"""
        try:
            self.sp.playlist(playlist_id)  # 해당 플레이리스트 정보 요청
            return True
        except spotipy.exceptions.SpotifyException:
            logging.warning(f"Invalid playlist ID: {playlist_id}")
            return False    
    
    def get_playlist_tracks(self, name, playlist_id):
        """플레이리스트에서 노래 가져오기"""
        logging.info(f"Fetching tracks for playlist: {name} (ID: {playlist_id})")
        try:
            tracks = self.sp.playlist_items(playlist_id)
            playlist_tracks = []
            while tracks:
                for item in tracks['items']:
                    track = item['track']
                    if track:  # Check if track exists
                        track_name = track['name']
                        artist_names = ", ".join(artist['name'] for artist in track['artists'])
                        logging.debug(f"Track: {track_name}, Artists: {artist_names}")
                        playlist_tracks.append({"Playlist Name": name, "Track Name": track_name, "Artists": artist_names})
                tracks = self.sp.next(tracks) if tracks['next'] else None
            return playlist_tracks
        except spotipy.exceptions.SpotifyException as e:
            logging.error(f"Error fetching playlist {name} (ID: {playlist_id}): {e}")
            return []
        
        
    
    def playlists_to_table(self, playlists, output_file="data/playlists.csv"):
        """플레이리스트 데이터를 CSV로 저장"""
        # 아직 테이블이 없어서 csv로 잘 만들어지는 지 확인
        # 나중에는 테이블로 연결되도록 만들면 될 듯
        all_tracks = []

        for name, playlist_id in playlists:
            # Fetch tracks for each playlist
            tracks = self.get_playlist_tracks(name, playlist_id)
            all_tracks.extend(tracks)

        # Save to CSV
        with open(output_file, mode="w", newline="", encoding="utf-8") as file:
            writer = csv.DictWriter(file, fieldnames=["Playlist Name", "Track Name", "Artists"])
            writer.writeheader()
            writer.writerows(all_tracks)

        print(f"CSV file created: {output_file}")

        
        
if __name__ == "__main__":
    spotipy_client = SpotifyClient()
    user_playlists = spotipy_client.get_user_playlists()
    featured_playlists = spotipy_client.get_featured_playlists()
    categories_playlists = spotipy_client.get_category_playlists()
    
    spotipy_client.playlists_to_table(user_playlists, output_file="data/user_playlists.csv")
    spotipy_client.playlists_to_table(featured_playlists, output_file="data/featured_playlists.csv")
    for category_name, playlists in categories_playlists.items():
        output_file = f"data/{category_name}_playlists.csv"
        for playlist in playlists:
            print(playlist)
            spotipy_client.playlists_to_table([category_name,playlist], output_file=output_file)
    
    

