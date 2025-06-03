# 🎧 How to Export Spotify Playlists to CSV

This section shows you how to export your Spotify playlists (including song title and artist name) into a `.csv` file compatible with the YouTube importer script.

---

## 🚀 Features

- ✅ Adds songs to a **specific YouTube Music playlist**
- ⏭️ Skips songs that already exist in the playlist
- 🗑️ Removes successfully added songs from the CSV
- ❌ Skips songs not found on YouTube Music
- 🔐 Uses secure OAuth 2.0 authentication
- 📦 CSV format: `Song Title, Artist`

---


---

## 🧰 Requirements

- A **Spotify account**
- A **Spotify Developer App** (free to set up)
- Python 3.7+
- The `spotipy` library (Python wrapper for Spotify Web API)

---

## 📦 Step-by-Step Setup

### 🔐 1. Create a Spotify Developer App

1. Go to:  
   🔗 [https://developer.spotify.com/dashboard](https://developer.spotify.com/dashboard)

2. Log in with your Spotify account

3. Click **"Create an App"**

4. Give it a name (e.g., `Playlist Exporter`), agree to the terms

5. After creation, click your app → Copy the following:
   - **Client ID**
   - **Client Secret**

---

### 🧪 2. Set a Redirect URI

1. Still in your app's dashboard, click **"Edit Settings"**

2. Under **Redirect URIs**, add:  
   http://127.0.0.1:8000/callback

3. Click **Save**

---

### 📥 3. Install Spotipy

Open terminal and run:

pip install spotipy

---

## 🧾 4. Run Python Script to Export Spotify Playlist

---

## 🎵 Spotify to YouTube Music Playlist Importer

This Python tool allows you to import songs from a CSV (exported from Spotify or elsewhere) directly into a **YouTube Music** playlist. It handles OAuth authentication, skips duplicates, and supports incremental importing by removing already-added songs from your CSV.


## 🛠 Prerequisites

- Python 3.7+
- A [Google Account](https://accounts.google.com/)
- Your CSV file of songs in the correct format (see below)

---

## 📋 CSV Format Example

```csv
Into Your Arms,Dev Bhawsar
Aaya Na Tu,Arjun Kanungo
MIDDLE OF THE NIGHT,Elley Duhé
```
Make sure your file is saved as spotify_playlist.csv.

---

## ⚙️ Step-by-Step Setup (Google Cloud Console)

✅ 1. Go to Google Cloud Console  
🔗 https://console.cloud.google.com/

🏗️ 2. Click on Select a Project dropdown on the top left  
Click "New Project"  
Give it a name like SpotifyToYouTubeMusic  
Click Create  

📡 3. Enable YouTube Data API  
Go to:  
🔗 https://console.cloud.google.com/apis/library  
Search for: YouTube Data API v3  
Click it → Click "Enable"  

🛡️ 4. Configure OAuth Consent Screen  
Go to:  
🔗 https://console.cloud.google.com/apis/credentials/consent  

Fill in:  
- App name: SpotifyToYouTubeMusic  
- User support email: Your email  
- Developer contact info: Your email again  

Select `"External" and click "Create"`

Click "Save and Continue" 

🔑 5. Create OAuth Credentials  
Go to:  
🔗 https://console.cloud.google.com/apis/credentials  
Click "Create Credentials" → Select "OAuth client ID"  
Application type: Desktop App  
Name it (e.g., "Desktop OAuth for YouTube")  
Click Create → then click Download JSON   

👤 6. Add Test Users
- On the left navigation bar, click **"Audience"**  
- Scroll down to the **"Test users"** section  
- Click **"Add Users"**  
- Enter the Gmail address you will use to run the script  
- Click **"Save and Continue"**, then **"Back to Dashboard"**




---

## 🧪 Install Dependencies

In your terminal or command prompt:

pip install google-auth-oauthlib google-api-python-client

---

## 📝 Update Your Python Script

Make sure to paste your playlist ID from YouTube Music into the script:

https://music.youtube.com/playlist?list=   `PLTeRxonoJibjq-IIpQZyW8zIhB_c3l4u0`  &si=y_I7wD20Y_No_q7n  
                                           ↑ This part is your ID
 
Update the variable:
TARGET_PLAYLIST_ID = 'PLxxxxxxxxxxxxxxxx'

---

## ▶️ Run the Script

python Youtube_importer.py  
It will open a browser window asking you to log in to Google and grant access.  
After authenticating, the script will begin importing songs.

---

## 💡 Script Behavior

| Status       | Behavior                                      |
|--------------|-----------------------------------------------|
| ✅ Success   | Song added to playlist and removed from CSV   |
| ⏭️ Duplicate  | Skipped if already exists in playlist         |
| ❌ Not Found | Skipped and left in CSV                       |
| 🔥 API Error | Script halts and logs the issue               |

---

## 📈 Quota Tips

Every search + insert costs API quota.  
You get 10,000 units/day by default.  
Searching costs 100 units; adding costs 50.  
You can monitor usage here:  
🔗 https://console.cloud.google.com/apis/dashboard

---

## 🤝 Contributing

Feel free to fork and improve! PRs are welcome if you’d like to:

- Add support for other platforms
- Improve matching accuracy
- Add better error handling

---