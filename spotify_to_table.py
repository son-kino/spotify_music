import spotipy
from spotipy.oauth2 import SpotifyOAuth
from dotenv import load_dotenv
import os

class SpotifyClient:
    def __init__(self):
        # Load environment variables
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
        # 이 부분은 추후 사용자가 넣은 플레이르스트로 수정하거나 제거할 필요 있음
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
        for name,id in categories_list:
            print(f"\nPlaylists for Category {name}:")
            category_playlist = []
            playlists = self.sp.category_playlists(category_id=id)
            for playlist in playlists['playlists']['items']:
                print(f"Name: {playlist['name']}, ID: {playlist['id']}")
                if playlist['name']:
                    category_playlist.append([name, id])
            categories_playlists[name] = category_playlist
        return categories_playlists
        
    def get_playlist_tracks(self, name, playlist_id):
        """플레이리스트에서 노래 가져오기"""
        print(f"\nTracks in Playlist {name}:")
        tracks = self.sp.playlist_items(playlist_id)
        while tracks:
            for item in tracks['items']:
                track = item['track']
                print(f"Track Name: {track['name']}, Artist(s): {', '.join(artist['name'] for artist in track['artists'])}")
            tracks = self.sp.next(tracks) if tracks['next'] else None
        
    def playlists_to_table(self, playlists):
        """테이블로 만드는 함수 추가"""
        # 아직 테이블이 없으니 일단 함수만 구현함
        for name,id in playlists:
            spotipy_client.get_playlist_tracks(name,id)
        
        
        
if __name__ == "__main__":
    spotipy_client = SpotifyClient()
    user_playlists = spotipy_client.get_user_playlists()
    featured_playlists = spotipy_client.get_featured_playlists()
    categories_playlists = spotipy_client.get_category_playlists()
    
    spotipy_client.playlists_to_table(user_playlists)
    spotipy_client.playlists_to_table(featured_playlists)
    for key, val in categories_playlists.items():
        spotipy_client.playlists_to_table(key,val)
    
