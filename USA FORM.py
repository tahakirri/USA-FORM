import os
import subprocess
import streamlit as st
from dotenv import load_dotenv
import spotipy
from spotipy.oauth2 import SpotifyOAuth

# Load environment variables
load_dotenv()

# Configure Spotify API
os.environ["SPOTIPY_CLIENT_ID"] = os.getenv("SPOTIPY_CLIENT_ID")
os.environ["SPOTIPY_CLIENT_SECRET"] = os.getenv("SPOTIPY_CLIENT_SECRET")
os.environ["SPOTIPY_REDIRECT_URI"] = os.getenv("SPOTIPY_REDIRECT_URI")

def get_playlist_name(playlist_url):
    """Extract playlist name using Spotipy"""
    sp = spotipy.Spotify(auth_manager=SpotifyOAuth(scope="playlist-read-private"))
    playlist_id = playlist_url.split("/")[-1].split("?")[0]
    playlist = sp.playlist(playlist_id)
    return playlist['name']

def download_playlist(playlist_url):
    """Download playlist using spotdl"""
    try:
        command = f"spotdl download {playlist_url}"
        process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        st.info("Download started... This may take a while depending on playlist size.")
        
        # Display progress
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        while True:
            output = process.stdout.readline()
            if output == b'' and process.poll() is not None:
                break
            if output:
                line = output.decode().strip()
                if "Downloaded" in line:
                    status_text.text(line)
                # Update progress (this is a simple approximation)
                if "Processing song" in line:
                    try:
                        current = int(line.split("[")[1].split("/")[0])
                        total = int(line.split("/")[1].split("]")[0])
                        progress_bar.progress(current / total)
                    except:
                        pass
        
        if process.returncode == 0:
            st.success("Download completed successfully!")
            return True
        else:
            st.error("Download failed. Please check the URL and try again.")
            return False
            
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")
        return False

# Streamlit UI
st.title("🎵 Spotify Playlist Downloader")
st.markdown("Download your Spotify playlists as high-quality MP3 files")

playlist_url = st.text_input("Enter Spotify Playlist URL:", placeholder="https://open.spotify.com/playlist/...")

if st.button("Download Playlist"):
    if playlist_url and "open.spotify.com/playlist/" in playlist_url:
        with st.spinner("Preparing download..."):
            try:
                playlist_name = get_playlist_name(playlist_url)
                st.subheader(f"Downloading: {playlist_name}")
                
                # Create download directory if it doesn't exist
                if not os.path.exists("downloads"):
                    os.makedirs("downloads")
                
                # Change to downloads directory
                os.chdir("downloads")
                
                # Start download
                if download_playlist(playlist_url):
                    st.balloons()
            except Exception as e:
                st.error(f"Error: {str(e)}")
    else:
        st.warning("Please enter a valid Spotify playlist URL")

st.markdown("---")
st.info("""
**Note:** 
- This downloads songs in the best available quality (typically 320kbps MP3)
- Large playlists may take significant time to download
- Songs are saved in a 'downloads' folder
- You need Spotify API credentials (free) for this to work
""")
