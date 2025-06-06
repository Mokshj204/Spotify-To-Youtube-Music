import os
import csv
import time
import tempfile
import shutil
import google_auth_oauthlib.flow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# Define API information
# Replace with the path to your Google API client secrets JSON file
# Example: r'C:\Users\YourName\Downloads\client_secret_XXXXXXXXXXXXXXXXXXXXXXXXXXXXXX.apps.googleusercontent.com.json'
CLIENT_SECRETS_FILE = r'path\to\your\client_secret.json'
SCOPES = ['https://www.googleapis.com/auth/youtube.force-ssl']

# Your target YouTube Music playlist ID
# Extract from the URL, e.g., 'PLTeRxonoJibjq-IIpQZyW8zIhB_c3l4u0' from 'https://music.youtube.com/playlist?list=PLTeRxonoJibjq-IIpQZyW8zIhB_c3l4u0'
TARGET_PLAYLIST_ID = 'YOUR_PLAYLIST_ID_HERE'

# Custom exception for quota errors
class QuotaExceededError(Exception):
    pass

# Authenticate and build the API client
def authenticate():
    """
    Authenticate with Google API using OAuth 2.0 and build the YouTube API client.
    Returns:
        A YouTube API client instance.
    """
    flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(
        CLIENT_SECRETS_FILE, SCOPES)
    credentials = flow.run_local_server(port=0)
    youtube = build('youtube', 'v3', credentials=credentials)
    return youtube

# Search for a song on YouTube
def search_song(youtube, song_title, artist):
    """
    Search YouTube for a song by title and artist, returning the first matching video ID.
    Args:
        youtube: YouTube API client instance.
        song_title: Title of the song.
        artist: Artist name.
    Returns:
        Video ID (str) if found, else None.
    """
    query = f'{song_title} {artist}'
    request = youtube.search().list(
        part='snippet',
        q=query,
        type='video',
        videoCategoryId='10',  # Music category
        maxResults=1
    )
    time.sleep(0.3)  # Respect API rate limits
    response = request.execute()

    if response['items']:
        return response['items'][0]['id']['videoId']
    return None

# Add song to playlist
def add_song_to_playlist(youtube, playlist_id, video_id):
    """
    Add a video to the specified YouTube playlist.
    Args:
        youtube: YouTube API client instance.
        playlist_id: ID of the target playlist.
        video_id: ID of the video to add.
    Returns:
        API response to verify success.
    """
    request = youtube.playlistItems().insert(
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
    )
    response = request.execute()
    time.sleep(0.2)  # Respect API rate limits
    return response

# Fetch all video IDs already in the playlist
def get_existing_video_ids(youtube, playlist_id):
    """
    Retrieve all video IDs in the specified playlist to avoid duplicates.
    Args:
        youtube: YouTube API client instance.
        playlist_id: ID of the target playlist.
    Returns:
        Set of video IDs.
    """
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
        time.sleep(0.2)  # Respect API rate limits
    return video_ids

# Helper function to safely print strings with potential encoding issues
def safe_print(message):
    """
    Print a message, replacing unencodable characters with '?'.
    Args:
        message (str): The message to print.
    """
    print(message.encode('ascii', errors='replace').decode('ascii'))

# Main logic to process CSV and update playlist
def process_csv_and_add_to_existing_playlist(csv_file_path):
    """
    Process a CSV file containing song titles and artists, add them to a YouTube playlist,
    and remove successfully added or duplicate songs from the CSV.
    Args:
        csv_file_path: Path to the CSV file with song title and artist columns.
    """
    youtube = authenticate()
    existing_video_ids = get_existing_video_ids(youtube, TARGET_PLAYLIST_ID)
    temp_file = tempfile.NamedTemporaryFile(mode='w', delete=False, newline='', encoding='utf-8')
    writer = csv.writer(temp_file)

    try:
        # Read CSV and process songs
        with open(csv_file_path, mode='r', encoding='utf-8') as file:
            reader = csv.reader(file)
            for row in reader:
                if len(row) < 2:
                    safe_print(f"[Error] Skipped invalid row: {row}")
                    writer.writerow(row)  # Keep invalid rows
                    continue
                song_title, artist = row
                try:
                    video_id = search_song(youtube, song_title, artist)
                    if not video_id:
                        safe_print(f"[Error] Not found: {song_title} by {artist}")
                        writer.writerow(row)  # Keep songs not found
                        continue
                    if video_id in existing_video_ids:
                        safe_print(f"[Skipped] Duplicate: {song_title} by {artist}")
                        # Do not write duplicates to the CSV (removes them)
                        continue

                    # Add song and verify success
                    response = add_song_to_playlist(youtube, TARGET_PLAYLIST_ID, video_id)
                    if response.get('id'):  # Verify the playlist item was created
                        safe_print(f"[Success] Added: {song_title} by {artist}")
                        existing_video_ids.add(video_id)
                    else:
                        safe_print(f"[Error] Failed to add: {song_title} by {artist}")
                        writer.writerow(row)
                except HttpError as e:
                    error_message = str(e)
                    safe_print(f"[Error] API Error: {e}")
                    writer.writerow(row)  # Keep songs in case of error
                    if 'quotaExceeded' in error_message.lower():
                        raise QuotaExceededError("YouTube API quota exceeded")
                except Exception as e:
                    safe_print(f"[Error] Unexpected error for {song_title} by {artist}: {e}")
                    writer.writerow(row)  # Keep songs on other errors

    except QuotaExceededError as e:
        safe_print(f"[Error] {e}. Stopping to preserve CSV. Try again after quota reset (12:30 PM IST tomorrow).")
    except Exception as e:
        safe_print(f"[Error] Fatal error during processing: {e}")
    finally:
        # Ensure temporary file is closed and moved
        temp_file.close()
        try:
            shutil.move(temp_file.name, csv_file_path)
            safe_print(f"Updated CSV at {csv_file_path}")
        except Exception as e:
            safe_print(f"[Error] Failed to update CSV: {e}")

# Your CSV file path
# Replace with the path to your CSV file
# Example: r'C:\Users\YourName\Desktop\Spotify Exporter\spotify_playlist.csv'
csv_file_path = r'path\to\your\spotify_playlist.csv'

try:
    process_csv_and_add_to_existing_playlist(csv_file_path)
except Exception as e:
    safe_print(f"[Error] Fatal error: {e}")

# Keep terminal open until a key is pressed
input("Press any key to exit...")
