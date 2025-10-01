from yt_dlp import YoutubeDL
import os
import sys
import platform
import subprocess
import zipfile
import tarfile
import urllib.request
import shutil

def get_base_path():
    """Get the base path - works for both script and executable."""
    if getattr(sys, 'frozen', False):
        # Running as compiled executable
        return os.path.dirname(sys.executable)
    else:
        # Running as script
        return os.path.dirname(os.path.abspath(__file__))

def get_ffmpeg_paths():
    """Get platform-specific FFmpeg paths (consistent bin folder)."""
    base_path = get_base_path()
    ffmpeg_dir = os.path.join(base_path, "ffmpeg", "bin")
    if platform.system() == "Windows":
        ffmpeg_exe = os.path.join(ffmpeg_dir, "ffmpeg.exe")
    else:
        ffmpeg_exe = os.path.join(ffmpeg_dir, "ffmpeg")
    return ffmpeg_exe, ffmpeg_dir

def check_ffmpeg():
    """Check if ffmpeg is installed and available."""
    ffmpeg_exe, ffmpeg_dir = get_ffmpeg_paths()

    if os.path.exists(ffmpeg_exe):
        os.environ["PATH"] = ffmpeg_dir + os.pathsep + os.environ["PATH"]
        print(f"Using FFmpeg from: {ffmpeg_exe}")
        return ffmpeg_exe
    else:
        # Try system FFmpeg
        try:
            result = subprocess.run(["ffmpeg", "-version"],
                                    capture_output=True,
                                    text=True,
                                    timeout=5)
            if result.returncode == 0:
                print("Using system FFmpeg")
                return "ffmpeg"
        except (subprocess.TimeoutExpired, FileNotFoundError):
            pass

        print("FFmpeg not found. Attempting to install...")
        install_ffmpeg()

        # Check again
        if os.path.exists(ffmpeg_exe):
            os.environ["PATH"] = ffmpeg_dir + os.pathsep + os.environ["PATH"]
            print(f"Using FFmpeg from: {ffmpeg_exe}")
            return ffmpeg_exe
        else:
            raise Exception("Failed to install FFmpeg. Please install manually.")

def install_ffmpeg():
    """Download and install FFmpeg in a cross-platform way using Python only."""
    base_path = get_base_path()
    ffmpeg_exe, ffmpeg_dir = get_ffmpeg_paths()

    if os.path.exists(ffmpeg_exe):
        print("FFmpeg is already installed.")
        return ffmpeg_exe

    system = platform.system()
    print(f"FFmpeg is missing. Downloading for {system}...")

    os.makedirs(ffmpeg_dir, exist_ok=True)

    try:
        if system == "Windows":
            ffmpeg_url = "https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip"
            ffmpeg_zip = os.path.join(base_path, "ffmpeg.zip")
            urllib.request.urlretrieve(ffmpeg_url, ffmpeg_zip)

            print("Extracting FFmpeg...")
            with zipfile.ZipFile(ffmpeg_zip, 'r') as zip_ref:
                # Extract to temp folder to locate the bin
                temp_extract = os.path.join(base_path, "ffmpeg_temp")
                zip_ref.extractall(temp_extract)

            # Find ffmpeg.exe inside extracted folder
            for root, dirs, files in os.walk(temp_extract):
                if "ffmpeg.exe" in files:
                    bin_src = root
                    break
            shutil.copy(os.path.join(bin_src, "ffmpeg.exe"), ffmpeg_dir)
            shutil.copy(os.path.join(bin_src, "ffplay.exe"), ffmpeg_dir)
            shutil.copy(os.path.join(bin_src, "ffprobe.exe"), ffmpeg_dir)

            shutil.rmtree(temp_extract, ignore_errors=True)
            os.remove(ffmpeg_zip)

        elif system == "Darwin":  # macOS
            ffmpeg_url = "https://evermeet.cx/ffmpeg/ffmpeg-6.1.zip"
            ffmpeg_zip = os.path.join(base_path, "ffmpeg.zip")
            urllib.request.urlretrieve(ffmpeg_url, ffmpeg_zip)

            print("Extracting FFmpeg...")
            with zipfile.ZipFile(ffmpeg_zip, 'r') as zip_ref:
                zip_ref.extractall(ffmpeg_dir)

            ffmpeg_extracted = os.path.join(ffmpeg_dir, "ffmpeg")
            os.chmod(ffmpeg_extracted, 0o755)  # make executable
            os.remove(ffmpeg_zip)

        else:  # Linux
            ffmpeg_url = "https://johnvansickle.com/ffmpeg/releases/ffmpeg-release-amd64-static.tar.xz"
            ffmpeg_tar = os.path.join(base_path, "ffmpeg.tar.xz")
            urllib.request.urlretrieve(ffmpeg_url, ffmpeg_tar)

            print("Extracting FFmpeg...")
            temp_extract = os.path.join(base_path, "ffmpeg_temp")
            with tarfile.open(ffmpeg_tar, 'r:xz') as tar_ref:
                tar_ref.extractall(temp_extract)

            # Find ffmpeg binary
            for root, dirs, files in os.walk(temp_extract):
                if "ffmpeg" in files:
                    bin_src = root
                    break
            shutil.copy(os.path.join(bin_src, "ffmpeg"), ffmpeg_dir)
            shutil.copy(os.path.join(bin_src, "ffplay"), ffmpeg_dir)
            shutil.copy(os.path.join(bin_src, "ffprobe"), ffmpeg_dir)

            shutil.rmtree(temp_extract, ignore_errors=True)
            os.remove(ffmpeg_tar)

        print("FFmpeg installed successfully.")
        return ffmpeg_exe

    except Exception as e:
        print(f"Error installing FFmpeg: {e}")
        print("Please install FFmpeg manually from https://ffmpeg.org/download.html")
        raise

def download_video(url, save_path='.'):
    try:
        print("Checking for FFmpeg...")
        ffmpeg_path = check_ffmpeg()
        print(f"FFmpeg path: {ffmpeg_path}")

        save_path = os.path.abspath(save_path)
        print(f"Save path: {save_path}")

        if not os.path.exists(save_path):
            print(f"Creating directory: {save_path}")
            os.makedirs(save_path)  

        options = {
            'format': 'bestvideo+bestaudio/best',
            'merge_output_format': 'mp4',
            'ffmpeg_location': ffmpeg_path,
            'outtmpl': os.path.join(save_path, '%(title)s.%(ext)s'),
            'verbose': True,
        }

        print("Starting download with options:", options)
        with YoutubeDL(options) as ydl:
            ydl.download([url])
        print(f"Download complete! Video saved to: {save_path}")
    except Exception as e:
        print(f"An error occurred: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    try:
        print(f"YouTube Downloader Starting on {platform.system()}...")
        video_url = input("Enter the YouTube video URL: ")
        output_path = input("Enter the folder path to save the video or press Enter for current directory: ") or '.'

        if output_path.startswith('"') and output_path.endswith('"'):
            output_path = output_path[1:-1]

        print(f"Downloading video from: {video_url}")
        print(f"Saving to: {output_path}")

        download_video(video_url, output_path)

        print("Program completed successfully.")
    except Exception as e:
        print(f"An error occurred: {e}")
        import traceback
        traceback.print_exc()
    
    # Keep window open so user sees result
    input("\nPress Enter to exit...")
