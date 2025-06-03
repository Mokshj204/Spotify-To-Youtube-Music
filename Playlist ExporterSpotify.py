import csv
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import os

# Spotify Developer app credentials
# Replace with your new Spotify app credentials from https://developer.spotify.com/dashboard
SPOTIPY_CLIENT_ID = 'YOUR_NEW_CLIENT_ID'
SPOTIPY_CLIENT_SECRET = 'YOUR_NEW_CLIENT_SECRET'
SPOTIPY_REDIRECT_URI = 'http://127.0.0.1:8000/callback'
SCOPE = 'playlist-read-private'

# Initialize Spotify client
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
    client_id=SPOTIPY_CLIENT_ID,
    client_secret=SPOTIPY_CLIENT_SECRET,
    redirect_uri=SPOTIPY_REDIRECT_URI,
    scope=SCOPE
))

# Playlist ID
PLAYLIST_ID = '0DXhMTjeF1C2V7lBWCvbvO'

# Initialize list to store song details
songs = []

# Helper function to safely print strings with potential encoding issues
def safe_print(message):
    """
    Print a message, replacing unencodable characters with '?'.
    Args:
        message
