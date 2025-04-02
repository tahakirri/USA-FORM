import streamlit as st
import subprocess
import os
import sys
from pathlib import Path

# Configure the app
st.set_page_config(page_title="Spotify Downloader", page_icon="🎵")
st.title("🎵 Spotify Track Downloader")
st.markdown("Download any Spotify track as an MP3")

# Check for required packages
try:
    import spotdl
except ImportError:
    st.error("""
    **spotdl is not installed!**
    
    Run this command in your terminal:
    ```
    pip install spotdl
    ```
    Then restart this app.
    """)
    st.stop()

# Sidebar with instructions
with st.sidebar:
    st.header("Instructions")
    st.markdown("""
    1. Copy a Spotify track URL (Share → Copy Song Link)
    2. Paste below and click "Download Track"
    3. Wait for completion (may take 1-2 minutes)
    """)
    st.markdown("---")
    st.markdown("**Requirements:**")
    st.code("""
    pip install spotdl
    # Plus FFmpeg installed on your system
    """)

def get_spotdl_command():
    """Determine the correct spotdl command format"""
    try:
        # Try direct spotdl command first
        subprocess.run(["spotdl", "--version"], check=True, capture_output=True)
        return "spotdl download {url}"
    except:
        # Fall back to python module format
        return f"{sys.executable} -m spotdl download {{url}}"

def find_downloaded_file():
    """Find the most recently downloaded MP3 file"""
    mp3_files = sorted(
        [f for f in os.listdir() if f.endswith(".mp3")],
        key=lambda x: os.path.getmtime(x),
        reverse=True
    )
    return mp3_files[0] if mp3_files else None

# Main app
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
                # Get the correct command format
                command_template = get_spotdl_command()
                command = command_template.format(url=spotify_url)
                
                # Run the command
                process = subprocess.run(
                    command,
                    shell=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True
                )
                
                if process.returncode == 0:
                    st.success("Download completed!")
                    
                    # Find and display the downloaded file
                    downloaded_file = find_downloaded_file()
                    if downloaded_file:
                        st.audio(downloaded_file)
                        
                        # Download button
                        with open(downloaded_file, "rb") as f:
                            st.download_button(
                                "Save MP3",
                                f.read(),
                                file_name=downloaded_file,
                                mime="audio/mp3"
                            )
                    else:
                        st.warning("Downloaded but file not found")
                else:
                    error_msg = process.stderr or "Unknown error occurred"
                    st.error(f"Download failed: {error_msg}")
                    st.code(process.stdout)  # Show full output for debugging
            
            except Exception as e:
                st.error(f"Error: {str(e)}")

# Footer
st.markdown("---")
st.caption("For personal use only. Please respect copyright laws.")
