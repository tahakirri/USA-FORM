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
        result = subprocess.run([sys.executable, "-m", "spotdl", "--version"],
                              capture_output=True, text=True)
        if result.returncode != 0:
            return False
        
        # Check FFmpeg
        result = subprocess.run(["ffmpeg", "-version"],
                              capture_output=True, text=True)
        return result.returncode == 0
    except:
        return False

def install_dependencies():
    """Install required packages with proper error handling"""
    try:
        # Install spotdl
        result = subprocess.run([sys.executable, "-m", "pip", "install", "spotdl"],
                              capture_output=True, text=True)
        if result.returncode != 0:
            error_msg = result.stderr if result.stderr else "Unknown error occurred"
            st.error(f"spotdl installation failed: {error_msg}")
            return False
        
        # Install FFmpeg based on OS
        if sys.platform == "linux":
            subprocess.run(["sudo", "apt-get", "update"], check=True)
            subprocess.run(["sudo", "apt-get", "install", "-y", "ffmpeg"], check=True)
        elif sys.platform == "darwin":
            subprocess.run(["brew", "install", "ffmpeg"], check=True)
        else:
            st.warning("Please install FFmpeg manually for your Windows system")
        
        return True
    except subprocess.CalledProcessError as e:
        error_msg = e.stderr if e.stderr else str(e)
        st.error(f"Dependency installation failed: {error_msg}")
        return False
    except Exception as e:
        st.error(f"Unexpected error: {str(e)}")
        return False

# Main app
def main():
    # Check dependencies
    if not check_dependencies():
        st.warning("Required dependencies not found!")
        if st.button("Install Dependencies Automatically"):
            if install_dependencies():
                st.success("Installation successful! Please restart the app.")
                st.balloons()
            else:
                st.error("""
                Automatic installation failed. Please install manually:
                ```
                pip install spotdl
                # And install FFmpeg for your system:
                # Linux: sudo apt install ffmpeg
                # Mac: brew install ffmpeg
                # Windows: Download from ffmpeg.org
                ```
                """)
        st.stop()

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
                    command = f"{sys.executable} -m spotdl download {spotify_url}"
                    result = subprocess.run(
                        command,
                        shell=True,
                        capture_output=True,
                        text=True
                    )
                    
                    if result.returncode == 0:
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
                        error_msg = result.stderr if result.stderr else "Unknown error"
                        st.error(f"Download failed: {error_msg}")
                        st.code(result.stdout)
                
                except Exception as e:
                    st.error(f"Error during download: {str(e)}")

if __name__ == "__main__":
    main()
