import os
import csv
import time
import google_auth_oauthlib.flow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# Define API information
#json file path similar to the one below
CLIENT_SECRETS_FILE = r'C:\Users\Pulin\Downloads\client_secret_331379160922-XXXXXXXXXXXXXXXXXXXXXXXXXXXXXX.apps.googleusercontent.com.json'
SCOPES = ['https://www.googleapis.com/auth/youtube.force-ssl']

# Your target YouTube Music playlist ID the end part after the ?
#https://music.youtube.com/playlist?list=  from here   "PLTeRxonoJibjq-IIpQZyW8zIhB_c3l4u0"     to here &si=y_I7wD20Y_No_q7n
TARGET_PLAYLIST_ID = 'PLTeRxonoJibjq-IIpQZyW8zIhB_c3l4u0'

# Authenticate and build the API client
def authenticate():
    flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(
        CLIENT_SECRETS_FILE, SCOPES)
    credentials = flow.run_local_server(port=0)
    youtube = build('youtube', 'v3', credentials=credentials)
    return youtube

# Search for a song on YouTube
def search_song(youtube, song_title, artist):
    query = f'{song_title} {artist}'
    request = youtube.search().list(
        part='snippet',
        q=query,
        type='video',
        videoCategoryId='10',
        maxResults=1
    )
    time.sleep(0.3)
    response = request.execute()

    if response['items']:
        return response['items'][0]['id']['videoId']
    return None

# Add song to playlist
def add_song_to_playlist(youtube, playlist_id, video_id):
    youtube.playlistItems().insert(
        part='snippet',
        body={
            'snippet': {
                'playlistId': playlist_id,
                'resourceId': {
                    'kind': 'youtube#video',
                    'videoId': video_id,
                }
            }
        }
    ).execute()
    time.sleep(0.2)

# Fetch all video IDs already in the playlist
def get_existing_video_ids(youtube, playlist_id):
    video_ids = set()
    next_page_token = None
    while True:
        request = youtube.playlistItems().list(
            part='snippet',
            playlistId=playlist_id,
            maxResults=50,
            pageToken=next_page_token
        )
        response = request.execute()

        for item in response['items']:
            video_id = item['snippet']['resourceId'].get('videoId')
            if video_id:
                video_ids.add(video_id)

        next_page_token = response.get('nextPageToken')
        if not next_page_token:
            break
        time.sleep(0.2)
    return video_ids

# Main logic to process CSV and update playlist
def process_csv_and_add_to_existing_playlist(csv_file_path):
    youtube = authenticate()
    existing_video_ids = get_existing_video_ids(youtube, TARGET_PLAYLIST_ID)

    with open(csv_file_path, mode='r', encoding='utf-8') as file:
        reader = csv.reader(file)
        for row in reader:
            if len(row) < 2:
                print(f"❌ Skipped invalid row: {row}")
                continue
            song_title, artist = row
            try:
                video_id = search_song(youtube, song_title, artist)
                if not video_id:
                    print(f"❌ Not found: {song_title} by {artist}")
                    continue
                if video_id in existing_video_ids:
                    print(f"⏭️ Skipped duplicate: {song_title} by {artist}")
                    continue

                add_song_to_playlist(youtube, TARGET_PLAYLIST_ID, video_id)
                print(f"✅ Added: {song_title} by {artist}")
                existing_video_ids.add(video_id)  # Add to memory to avoid rechecking
            except HttpError as e:
                print(f"❌ API Error: {e}")
                break

    print("🎉 Done updating playlist!")

# Your CSV file path
csv_file_path = r'C:\Users\Pulin\Desktop\Spotify Exporter\Spotify-To-CSV-Exporter\spotify_playlist.csv'
process_csv_and_add_to_existing_playlist(csv_file_path)
