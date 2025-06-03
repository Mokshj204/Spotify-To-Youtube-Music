import csv
import spotipy
from spotipy.oauth2 import SpotifyOAuth

# Your Spotify Developer app credentials
#Wont Work because i am deleting the app from spotify developer dashboard
# get new credentials for it to work
SPOTIPY_CLIENT_ID = ''
SPOTIPY_CLIENT_SECRET = ''
SPOTIPY_REDIRECT_URI = 'http://127.0.0.1:8000/callback'
scope = 'playlist-read-private'

sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
    client_id=SPOTIPY_CLIENT_ID,
    client_secret=SPOTIPY_CLIENT_SECRET,
    redirect_uri=SPOTIPY_REDIRECT_URI,
    scope=scope
))

sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
    client_id=SPOTIPY_CLIENT_ID,
    client_secret=SPOTIPY_CLIENT_SECRET,
    redirect_uri=SPOTIPY_REDIRECT_URI,
    scope=scope
))

# Playlist ID (replace this with your actual playlist ID) only the end part after the ? 
playlist_id = '0DXhMTjeF1C2V7lBWCvbvO'

# Initialize list to store song details
songs = []

# Function to fetch all tracks (handle pagination)
def fetch_all_tracks(playlist_id):
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
fetch_all_tracks(playlist_id)

# Save to CSV
with open('spotify_playlist.csv', 'w', newline='', encoding='utf-8') as f:
    writer = csv.writer(f)
    writer.writerow(['Title', 'Artist'])
    writer.writerows(songs)

print("✅ Playlist exported to spotify_playlist.csv!")
