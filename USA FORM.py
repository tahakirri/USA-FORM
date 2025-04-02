import streamlit as st
import subprocess
import os

# App title
st.title("🎵 Spotify Track Downloader")
st.markdown("Download any Spotify track as an MP3 using `spotdl`.")

# Input: Spotify Track URL
spotify_url = st.text_input(
    "Enter Spotify Track URL:",
    placeholder="e.g., https://open.spotify.com/track/..."
)

# Download button
if st.button("Download Track"):
    if not spotify_url:
        st.error("Please enter a Spotify URL!")
    else:
        try:
            # Run spotdl download command
            command = f"spotdl download {spotify_url}"
            
            with st.spinner("Downloading track..."):
                result = subprocess.run(
                    command,
                    shell=True,
                    capture_output=True,
                    text=True
                )
            
            if result.returncode == 0:
                st.success("Track downloaded successfully! 🎶")
                
                # Find the downloaded file (assuming MP3)
                downloaded_files = [f for f in os.listdir() if f.endswith(".mp3")]
                if downloaded_files:
                    st.audio(downloaded_files[0])
                    st.download_button(
                        "Download MP3",
                        data=open(downloaded_files[0], "rb").read(),
                        file_name=downloaded_files[0],
                        mime="audio/mp3"
                    )
                else:
                    st.warning("File downloaded but not found in directory.")
            else:
                st.error(f"Error downloading track: {result.stderr}")
        
        except Exception as e:
            st.error(f"An error occurred: {e}")

# Instructions
st.markdown("### How to Use:")
st.markdown("""
1. Copy a Spotify track URL (e.g., `https://open.spotify.com/track/...`).
2. Paste it above and click **Download Track**.
3. Wait for the download to finish, then play or save the MP3.
""")

# Requirements note
st.warning("""
**Requirements:**
- Python & `spotdl` installed (`pip install spotdl`).
- FFmpeg must be installed for audio conversion.
- Run this app in a terminal where `spotdl` is available.
""")
