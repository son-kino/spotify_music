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
        """사용자의 플레이리스트 가져오기"""
        print("\nUser Playlists:")
        playlists = self.sp.current_user_playlists()
        user_playlists = []
        while playlists:
            for playlist in playlists['items']:
                print(f"Name: {playlist['name']}, ID: {playlist['id']}")
                user_playlists.append([playlist['name'],playlist['id']])
            playlists = self.sp.next(playlists) if playlists['next'] else None
        return user_playlists
    
    
    def get_featured_playlists(self):
        """전 세계적이거나 지역적으로 인기 있는 플레이리스트, 특정 계절 또는 테마에 맞춘 플레이리스트 가져오기"""
        print("\nFeatured Playlists:")
        featured_playlists = self.sp.featured_playlists()
        for playlist in featured_playlists['playlists']['items']:
            print(f"Name: {playlist['name']}, ID: {playlist['id']}")
        
    def get_playlist_tracks(self, name, playlist_id):
        """플레이리스트에서 노래 가져오기"""
        print(f"\nTracks in Playlist {name}:")
        tracks = self.sp.playlist_items(playlist_id)
        while tracks:
            for item in tracks['items']:
                track = item['track']
                print(f"Track Name: {track['name']}, Artist(s): {', '.join(artist['name'] for artist in track['artists'])}")
            tracks = self.sp.next(tracks) if tracks['next'] else None
        print(tracks)
        
    def play_list_to_csv
        
        
        
if __name__ == "__main__":
    spotipy_client = SpotifyClient()
    user_playlists = spotipy_client.get_user_playlists()
    for name,id in user_playlists:
        spotipy_client.get_playlist_tracks(name, id)
    