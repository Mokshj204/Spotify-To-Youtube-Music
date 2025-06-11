import os
import csv
import time
import tempfile
import shutil
import google_auth_oauthlib
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# Define API information
# Replace with the path to your Google API client secrets JSON file
# Example: r'C:\Users\YourUsername\Downloads\client_secret_XXXXXXXXXXXXXXXXXX.apps.googleusercontent.com.json'
CLIENT_SECRETS_FILE = r'path\to\your\client_secret.json'
SCOPES = ['https://www.googleapis.com/auth/youtube.force-ssl']

# Your target YouTube Music playlist ID
# Example: 'PLTWXyZqR1234567890' from 'https://music.youtube.com/playlist?list=PLTWXyZqR1234567890'
TARGET_PLAYLIST_ID = 'YOUR_PLAYLIST_ID'

# Custom exception for quota errors
class QuotaExceededError(Exception):
    pass

# Global flag to track quota
QUOTA_EXCEEDED = False

# Authenticate and build Spotify Client
def authenticate():
    """
    Authenticate with Google API using OAuth 2.0 and build the YouTube API client.
    Returns:
        Authenticated YouTube Client
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
        str: Video ID or None if not found.
    """
    global QUOTA_EXCEEDED
    if QUOTA_EXCEEDED:
        raise QuotaExceededError("Quota already exceeded")
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

    if response.get('items'):
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
    global QUOTA_EXCEEDED
    if QUOTA_EXCEEDED:
        raise QuotaExceededError("Quota already exceeded")
    request = youtube.playListItems().insert(
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
    time.sleep(0.2)
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
    global QUOTA_EXCEEDED
    if QUOTA_EXCEEDED:
        raise QuotaExceededError("Quota already exceeded")
    video_ids = set()
    next_page_token = None
    while True:
        try:
            request = youtube.playlistItems().list(
                part='snippet',
                playlistId=playlist_id,
                maxResults=50,
                pageToken=next_page_token
            )
            response = request.execute()
            
            for item in response.get('items', []):
                video_id = item['snippet']['resourceId'].get('videoId')
                if video_id:
                    video_ids.add(video_id)
                
                next_page_token = response.get('nextPageToken')
                if not next_page_token:
                    break
            time.sleep(0.2)
        except HttpError as e:
            error_message = str(e).lower()
            if 'quotaexceeded' in error_message:
                QUOTA_EXCEEDED = True
                raise QuotaExceededError("YouTube API quota exceeded during playlist retrieval")
            raise
    return video_ids

# Helper function to safely print strings with potential encoding issues
def safe_print(message):
    """
    Print a message, replacing unencodable characters with '?'.
    Parameters:
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
    global QUOTA_EXCEEDED
    youtube = authenticate()
    temp_file = tempfile.NamedTemporaryFile(mode='w', delete=False, newline='', encoding='utf-8')
    writer = csv.writer(temp_file)

    try:
        # Copy all rows to temp file initially
        with open(csv_file_path, mode='r', encoding='utf-8') as file:
            reader = csv.reader(file)
            for row in reader:
                writer.writerow(row)

        # Get existing video IDs
        existing_video_ids = get_existing_video_ids(youtube, TARGET_PLAYLIST_ID)

        # Reopen temp file for reading and create new temp file for writing
        temp_file.close()
        new_temp_file = tempfile.NamedTemporaryFile(mode='w', delete=False, newline='', encoding='utf-8')
        writer = csv.writer(new_temp_file)

        # Process songs
        with open(temp_file.name, mode='r', encoding='utf-8') as file:
            reader = csv.reader(file)
            for row in reader:
                if len(row) < 2:
                    safe_print(f"[Error] Skipped invalid row: {row}")
                    writer.writerow(row)  # Keep invalid rows
                    continue
                song_title, artist = row
                try:
                    if QUOTA_EXCEEDED:
                        writer.writerow(row)
                        continue
                    video_id = search_song(youtube, song_title, artist)
                    if not video_id:
                        safe_print(f"[Error] Not found: {song_title} by {artist}")
                        writer.writerow(row)  # Keep songs not found
                        continue
                    if video_id in existing_video_ids:
                        safe_print(f"[Skipped] Duplicate: {song_title} by {artist}")
                        # Do not write duplicates to CSV (removes them)
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
                    error_message = str(e).lower()
                    safe_print(f"[Error] API Error: {e}")
                    writer.writerow(row)  # Keep the song
                    if 'quotaexceeded' in error_message:
                        QUOTA_EXCEEDED = True
                        raise QuotaExceededError("YouTube API quota exceeded")
                except QuotaExceededError:
                    writer.writerow(row)  # Keep the song
                    continue
                except Exception as e:
                    safe_print(f"[Error] Unexpected error for {song_title} by {artist}: {e}")
                    writer.writerow(row)  # Keep the song

    except QuotaExceededError:
        safe_print(f"[Error] {str(e)}. Stopping to preserve CSV. Try again after quota reset (12:30 PM IST tomorrow).")
    except Exception as e:
        safe_print(f"[Error] Fatal error during processing: {e}")
    finally:
        # Ensure temporary files are closed and moved
        temp_file.close()
        new_temp_file.close()
        try:
            shutil.move(new_temp_file.name, csv_file_path)
            safe_print(f"[Success] Updated CSV at {csv_file_path}")
        except Exception as e:
            safe_print(f"[Error] Failed to update CSV: {e}")
        finally:
            try:
                os.remove(temp_file.name)
            except:
                pass

# Your CSV file path
# Replace with the path to your CSV file
# Example: r'C:\Users\YourUsername\Documents\spotify_playlist.csv'
csv_file_path = r'path\to\your\spotify_playlist.csv'

try:
    process_csv_and_add_to_existing_playlist(csv_file_path)
except Exception as e:
    safe_print(f"[Error] Fatal error: {e}")

# Keep terminal open until a key is pressed
input("Press any key to exit...")
