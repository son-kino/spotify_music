import spotipy
from spotipy.oauth2 import SpotifyOAuth
from dotenv import load_dotenv
import os

class SpotifyClient:
    def __init__(self):
        # Load environment variables
        load_dotenv()

        self.client_id = os.getenv("CLIENT_ID")
        self.client_secret = os.getenv("CLIENT_SECRET")
        self.redirect_uri = os.getenv("REDIRECT_URI")

        # Spotipy initialization
        self.scope = "playlist-read-private playlist-read-collaborative"
        self.sp = spotipy.Spotify(
            auth_manager=SpotifyOAuth(
                client_id=self.client_id,
                client_secret=self.client_secret,
                redirect_uri=self.redirect_uri,
                scope=self.scope,
            )
        )

    def get_user_playlists(self):
        """Fetch and print user's playlists."""
        print("\nUser Playlists:")
        playlists = self.sp.current_user_playlists()
        print()
        while playlists:
            for playlist in playlists['items']:
                print(f"Name: {playlist['name']}, ID: {playlist['id']}")
            playlists = self.sp.next(playlists) if playlists['next'] else None
        return playlists

    def get_playlist_tracks(self, playlist_id):
        """Fetch and print tracks from a specific playlist."""
        print(f"\nTracks in Playlist {playlist_id}:")
        tracks = self.sp.playlist_items(playlist_id)
        while tracks:
            for item in tracks['items']:
                track = item['track']
                print(f"Track Name: {track['name']}, Artist(s): {', '.join(artist['name'] for artist in track['artists'])}")
            tracks = self.sp.next(tracks) if tracks['next'] else None
        return tracks

    def get_featured_playlists(self):
        """Fetch and print Spotify's featured playlists."""
        print("\nFeatured Playlists:")
        featured_playlists = self.sp.featured_playlists()
        for playlist in featured_playlists['playlists']['items']:
            print(f"Name: {playlist['name']}, ID: {playlist['id']}")

    def get_category_playlists(self, category_id):
        """Fetch and print playlists for a specific category."""
        print(f"\nPlaylists for Category {category_id}:")
        playlists = self.sp.category_playlists(category_id=category_id)
        for playlist in playlists['playlists']['items']:
            print(f"Name: {playlist['name']}, ID: {playlist['id']}")

    def list_categories(self):
        """List available categories."""
        print("\nAvailable Categories:")
        categories = self.sp.categories()
        for category in categories['categories']['items']:
            print(f"Category Name: {category['name']}, ID: {category['id']}")

if __name__ == "__main__":
    # Instantiate the client
    spotify_client = SpotifyClient()

    # 1. Fetch user playlists
    spotify_client.get_user_playlists()

    # 2. Fetch Spotify's featured playlists (popular charts)
    spotify_client.get_featured_playlists()

    # 3. List categories for genre/situation
    spotify_client.list_categories()

    # 4. Fetch playlists for a specific category (replace with actual category ID)
    category_id = input("\nEnter a category ID to fetch playlists: ").strip()
    spotify_client.get_category_playlists(category_id)