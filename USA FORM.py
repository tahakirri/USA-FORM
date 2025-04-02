import streamlit as st
import subprocess
import os
from pathlib import Path

# Configure the app
st.set_page_config(page_title="Spotify Downloader", page_icon="🎵")
st.title("🎵 Spotify Track Downloader")
st.markdown("Download any Spotify track as an MP3 using `spotdl`.")

# Sidebar with instructions
with st.sidebar:
    st.header("Instructions")
    st.markdown("""
    1. Copy a Spotify track URL (Share → Copy Song Link)
    2. Paste it in the input box
    3. Click "Download Track"
    4. Wait for completion, then play/download
    """)
    st.markdown("---")
    st.markdown("**Note:** Requires Python, spotdl, and FFmpeg installed.")

# Input box for Spotify URL
spotify_url = st.text_input(
    "Enter Spotify Track URL:",
    placeholder="https://open.spotify.com/track/...",
    key="url_input"
)

def find_downloaded_file():
    """Find the most recently downloaded MP3 file"""
    mp3_files = sorted(
        [f for f in os.listdir() if f.endswith(".mp3")],
        key=lambda x: os.path.getmtime(x),
        reverse=True
    )
    return mp3_files[0] if mp3_files else None

if st.button("Download Track", type="primary"):
    if not spotify_url:
        st.error("Please enter a Spotify URL!")
    else:
        with st.spinner("Downloading track... This may take a minute"):
            try:
                # Use python -m spotdl to ensure it runs correctly
                command = f"python -m spotdl download {spotify_url}"
                
                # Run the command
                process = subprocess.Popen(
                    command,
                    shell=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    universal_newlines=True
                )
                
                # Display progress in real-time
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                while True:
                    output = process.stdout.readline()
                    if output == '' and process.poll() is not None:
                        break
                    if output:
                        status_text.text(output.strip())
                        if "Downloaded" in output:
                            progress_bar.progress(100)
                
                # Check for errors
                return_code = process.poll()
                if return_code == 0:
                    st.success("Download completed successfully!")
                    
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
                        st.warning("File downloaded but not found.")
                else:
                    st.error(f"Error downloading track: {process.stderr.read()}")
            
            except Exception as e:
                st.error(f"An error occurred: {str(e)}")

# Footer
st.markdown("---")
st.caption("Note: This tool is for personal use only. Please respect copyright laws.")
