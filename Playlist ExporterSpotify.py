import csv
import spotipy
from spotipy.oauth2 import SpotifyOAuth

# Spotify Developer app credentials
# Replace with your Spotify app credentials from https://developer.spotify.com/dashboard
SPOTIPY_CLIENT_ID = 'YOUR_CLIENT_ID'
SPOTIPY_CLIENT_SECRET = 'YOUR_CLIENT_SECRET'
SPOTIPY_REDIRECT_URI = 'YOUR_REDIRECT_URI'  # Example: 'http://127.0.0.1:8000/callback'
SCOPE = 'playlist-read-private'

# Initialize Spotify client
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
    client_id=SPOTIPY_CLIENT_ID,
    client_secret=SPOTIPY_CLIENT_SECRET,
    redirect_uri=SPOTIPY_REDIRECT_URI,
    scope=SCOPE
))

# Playlist ID
# Replace with your Spotify playlist ID (part after ?list= in the playlist URL)
# Example: '0DXhMTjeF1C2V7lBWCvbvO' from 'https://open.spotify.com/playlist/0DXhMTjeF1C2V7lBWCvbvO'
PLAYLIST_ID = 'YOUR_PLAYLIST_ID'

# Initialize list to store song details
songs = []

# Function to fetch all tracks (handle pagination)
def fetch_all_tracks(playlist_id):
    """
    Fetch all tracks from a Spotify playlist, handling pagination.
    Args:
        playlist_id (str): The Spotify playlist ID.
    Returns:
        None. Populates the global 'songs' list with [track_name, artists] pairs.
    """
    offset = 0
    while True:
        results = sp.playlist_tracks(playlist_id, offset=offset)
        tracks = results['items']
        
        for item in tracks:
            track = item['track']
            track_name = track['name']
            artists = ', '.join([artist['name'] for artist in track['artists']])
            songs.append([track_name, artists])
        
        # Check if there are more tracks to fetch
        if len(tracks) < 100:
            break
        else:
            offset += 100  # Move to the next set of tracks

# Fetch all tracks from the playlist
fetch_all_tracks(PLAYLIST_ID)

# Save to CSV
with open('spotify_playlist.csv', 'w', newline='', encoding='utf-8') as f:
    writer = csv.writer(f)
    writer.writerow(['Title', 'Artist'])
    writer.writerows(songs)

print("[Success] Playlist exported to spotify_playlist.csv!")
