import spotipy
from spotipy.oauth2 import SpotifyOAuth
from dotenv import load_dotenv
import os
import csv

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
        """Fetch and return user's playlists."""
        print("\nFetching User Playlists...")
        playlists = self.sp.current_user_playlists()
        all_playlists = []
        while playlists:
            for playlist in playlists['items']:
                all_playlists.append({
                    "name": playlist['name'],
                    "id": playlist['id']
                })
            playlists = self.sp.next(playlists) if playlists['next'] else None
        return all_playlists

    def get_playlist_tracks(self, playlist_id):
        """Fetch and return tracks from a specific playlist."""
        print(f"\nFetching Tracks for Playlist ID: {playlist_id}")
        tracks = self.sp.playlist_items(playlist_id)
        all_tracks = []
        while tracks:
            for item in tracks['items']:
                track = item['track']
                if track:  # Ensure track data is available
                    all_tracks.append({
                        "track_name": track['name'],
                        "artist_names": ", ".join(artist['name'] for artist in track['artists']),
                        "album_name": track['album']['name'],
                        "track_id": track['id'],
                        "track_url": track['external_urls']['spotify']
                    })
            tracks = self.sp.next(tracks) if tracks['next'] else None
        return all_tracks

    def save_tracks_to_csv(self, tracks, filename="playlist_tracks.csv"):
        """Save track data to a CSV file."""
        print(f"\nSaving Tracks to {filename}...")
        with open(filename, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.DictWriter(file, fieldnames=["track_name", "artist_names", "album_name", "track_id", "track_url"])
            writer.writeheader()
            writer.writerows(tracks)
        print(f"Tracks saved to {filename} successfully.")

if __name__ == "__main__":
    # Instantiate the client
    spotify_client = SpotifyClient()

    # Fetch user playlists
    playlists = spotify_client.get_user_playlists()
    print("\nUser Playlists:")
    for idx, playlist in enumerate(playlists):
        print(f"{idx + 1}. {playlist['name']} (ID: {playlist['id']})")

    # Get playlist ID from the user
    choice = int(input("\nEnter the number of the playlist to fetch tracks from: ")) - 1
    if 0 <= choice < len(playlists):
        selected_playlist = playlists[choice]
        print(f"Selected Playlist: {selected_playlist['name']} (ID: {selected_playlist['id']})")

        # Fetch tracks and save to CSV
        tracks = spotify_client.get_playlist_tracks(selected_playlist['id'])
        spotify_client.save_tracks_to_csv(tracks)
    else:
        print("Invalid choice. Exiting...")