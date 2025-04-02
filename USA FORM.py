import streamlit as st
import subprocess
import os
import sys
from pathlib import Path

# Configure the app
st.set_page_config(page_title="Spotify Downloader", page_icon="🎵")
st.title("🎵 Spotify Track Downloader")

def check_dependencies():
    """Check if spotdl and FFmpeg are installed"""
    try:
        # Check spotdl
        subprocess.run([sys.executable, "-m", "spotdl", "--version"], 
                      capture_output=True, check=True)
        
        # Check FFmpeg
        subprocess.run(["ffmpeg", "-version"],
                      capture_output=True, check=True)
        return True
    except:
        return False

def install_dependencies():
    """Install required packages"""
    with st.spinner("Installing dependencies (this may take a minute)..."):
        try:
            # Install spotdl
            subprocess.run([sys.executable, "-m", "pip", "install", "spotdl"],
                          check=True)
            
            # Install FFmpeg based on OS
            if sys.platform == "linux":
                subprocess.run(["sudo", "apt-get", "update"], check=True)
                subprocess.run(["sudo", "apt-get", "install", "-y", "ffmpeg"], check=True)
            elif sys.platform == "darwin":
                subprocess.run(["brew", "install", "ffmpeg"], check=True)
            
            return True
        except subprocess.CalledProcessError as e:
            st.error(f"Installation failed: {e.stderr.decode()}")
            return False

# Check if dependencies are installed
if not check_dependencies():
    st.warning("Required dependencies not found!")
    if st.button("Install Dependencies Automatically"):
        if install_dependencies():
            st.success("Installation successful! Please restart the app.")
            st.experimental_rerun()
        else:
            st.error("""
            Automatic installation failed. Please install manually:
            ```
            pip install spotdl
            # And install FFmpeg for your system
            ```
            """)
    st.stop()

# Main app functionality
def find_downloaded_file():
    """Find the most recently downloaded MP3 file"""
    mp3_files = sorted(
        [f for f in os.listdir() if f.endswith(".mp3")],
        key=lambda x: os.path.getmtime(x),
        reverse=True
    )
    return mp3_files[0] if mp3_files else None

spotify_url = st.text_input(
    "Paste Spotify Track URL:",
    placeholder="https://open.spotify.com/track/...",
    key="url_input"
)

if st.button("Download Track", type="primary"):
    if not spotify_url:
        st.error("Please enter a Spotify URL!")
    else:
        with st.spinner("Downloading... (This may take 1-2 minutes)"):
            try:
                # Use the most reliable command format
                command = f"{sys.executable} -m spotdl download {spotify_url}"
                
                process = subprocess.run(
                    command,
                    shell=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True
                )
                
                if process.returncode == 0:
                    st.success("Download completed!")
                    
                    downloaded_file = find_downloaded_file()
                    if downloaded_file:
                        st.audio(downloaded_file)
                        with open(downloaded_file, "rb") as f:
                            st.download_button(
                                "Save MP3",
                                f.read(),
                                file_name=downloaded_file,
                                mime="audio/mp3"
                            )
                    else:
                        st.warning("File downloaded but not found in directory.")
                else:
                    st.error(f"Download failed: {process.stderr}")
                    st.code(process.stdout)
            
            except Exception as e:
                st.error(f"Error: {str(e)}")

# Instructions
with st.expander("How to use"):
    st.markdown("""
    1. Paste a Spotify track URL (from Share → Copy Song Link)
    2. Click "Download Track"
    3. Wait for completion (usually 1-2 minutes)
    4. Play or download the MP3 file
    """)

# System information
with st.expander("System Info"):
    st.code(f"""
    Python: {sys.version}
    System: {sys.platform}
    spotdl: {subprocess.run([sys.executable, "-m", "spotdl", "--version"], 
                          capture_output=True, text=True).stdout}
    FFmpeg: {subprocess.run(["ffmpeg", "-version"], 
                          capture_output=True, text=True).stdout.splitlines()[0]}
    """)
