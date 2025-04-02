import streamlit as st
import subprocess
import os
import sys
from pathlib import Path

# App Configuration
st.set_page_config(
    page_title="Spotify Track Downloader",
    page_icon="🎵",
    layout="centered"
)

# Custom CSS for better appearance
st.markdown("""
<style>
    .stDownloadButton button {
        width: 100%;
    }
    .stSpinner > div {
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)

def is_installed(package):
    """Check if a Python package is installed"""
    try:
        __import__(package)
        return True
    except ImportError:
        return False

def check_ffmpeg():
    """Check if FFmpeg is available"""
    try:
        result = subprocess.run(
            ["ffmpeg", "-version"],
            capture_output=True,
            text=True
        )
        return result.returncode == 0
    except:
        return False

def install_spotdl():
    """Install spotdl package"""
    with st.spinner("Installing spotdl..."):
        try:
            subprocess.run(
                [sys.executable, "-m", "pip", "install", "spotdl"],
                check=True,
                capture_output=True,
                text=True
            )
            return True
        except subprocess.CalledProcessError as e:
            st.error(f"Failed to install spotdl: {e.stderr if e.stderr else 'Unknown error'}")
            return False

def download_track(url):
    """Download a Spotify track"""
    try:
        result = subprocess.run(
            [sys.executable, "-m", "spotdl", "download", url],
            capture_output=True,
            text=True,
            timeout=300  # 5 minute timeout
        )
        
        if result.returncode == 0:
            # Find the newest MP3 file in directory
            mp3_files = sorted(
                [f for f in os.listdir() if f.endswith(".mp3")],
                key=lambda x: os.path.getmtime(x),
                reverse=True
            )
            
            if mp3_files:
                return mp3_files[0]
        return None
    except Exception as e:
        st.error(f"Download failed: {str(e)}")
        return None

# Main App UI
st.title("🎧 Spotify Track Downloader")
st.markdown("Download any Spotify track as an MP3 file")

# Dependency Check
if not is_installed("spotdl") or not check_ffmpeg():
    st.warning("Required dependencies are missing!")
    
    if st.button("Install Dependencies Automatically"):
        if install_spotdl():
            st.success("spotdl installed successfully!")
            if not check_ffmpeg():
                st.warning("""
                FFmpeg is still required. Please install it manually:
                - **Windows**: Download from [ffmpeg.org](https://ffmpeg.org/)
                - **Mac**: `brew install ffmpeg`
                - **Linux**: `sudo apt install ffmpeg`
                """)
            st.experimental_rerun()
    else:
        st.info("""
        You need to install:
        ```
        pip install spotdl
        ```
        And FFmpeg for your operating system.
        """)
        st.stop()

# Main Download Interface
with st.form("download_form"):
    url = st.text_input(
        "Spotify Track URL",
        placeholder="https://open.spotify.com/track/...",
        help="Right-click on a Spotify track and select 'Copy Song Link'"
    )
    
    submitted = st.form_submit_button("Download Track", type="primary")

if submitted:
    if not url:
        st.error("Please enter a Spotify URL")
    else:
        with st.spinner("Downloading track... This may take a few minutes"):
            downloaded_file = download_track(url)
            
            if downloaded_file:
                st.success("Download complete!")
                
                # Display audio player
                st.audio(downloaded_file)
                
                # Download button
                with open(downloaded_file, "rb") as f:
                    st.download_button(
                        "Save MP3 File",
                        f.read(),
                        file_name=downloaded_file,
                        mime="audio/mp3",
                        key="download_mp3"
                    )
            else:
                st.error("Failed to download track. Please check the URL and try again.")

# Instructions
with st.expander("ℹ️ How to use"):
    st.markdown("""
    1. Find a track on Spotify
    2. Right-click the track → Share → Copy Song Link
    3. Paste the URL above and click Download
    4. Wait for processing, then download your MP3
    """)

# Footer
st.markdown("---")
st.caption("Note: This tool is for personal use only. Please respect copyright laws.")
