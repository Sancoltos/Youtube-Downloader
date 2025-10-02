import os
import platform
import ssl
import urllib.request
import zipfile
import tarfile
import shutil
import subprocess
from yt_dlp import YoutubeDL


def check_ffmpeg():
    """Ensure FFmpeg is installed and return the path."""
    base_path = os.path.dirname(os.path.abspath(__file__))
    ffmpeg_dir = os.path.join(base_path, "ffmpeg", "bin")
    os.makedirs(ffmpeg_dir, exist_ok=True)

    system = platform.system()
    exe = "ffmpeg.exe" if system == "Windows" else "ffmpeg"
    ffmpeg_path = os.path.join(ffmpeg_dir, exe)

    if os.path.exists(ffmpeg_path):
        print(f"FFmpeg already installed: {ffmpeg_path}")
        return ffmpeg_path

    print("FFmpeg not found. Attempting to install...")

    # SSL fix for macOS certificate issue
    try:
        ssl.create_default_context()
    except ssl.SSLError:
        print("SSL certificate issue detected. Using unverified context...")
        ssl._create_default_https_context = ssl._create_unverified_context

    try:
        if system == "Windows":
            url = "https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip"
            zip_path = os.path.join(base_path, "ffmpeg.zip")
            urllib.request.urlretrieve(url, zip_path)

            with zipfile.ZipFile(zip_path, "r") as zip_ref:
                for member in zip_ref.namelist():
                    if member.endswith("ffmpeg.exe"):
                        zip_ref.extract(member, ffmpeg_dir)
                        src = os.path.join(ffmpeg_dir, member)
                        shutil.move(src, ffmpeg_path)
                        break
            os.remove(zip_path)

        elif system == "Darwin":  # macOS
            url = "https://evermeet.cx/ffmpeg/ffmpeg-6.1.zip"
            zip_path = os.path.join(base_path, "ffmpeg.zip")
            urllib.request.urlretrieve(url, zip_path)

            with zipfile.ZipFile(zip_path, "r") as zip_ref:
                for member in zip_ref.namelist():
                    if member.endswith("ffmpeg"):
                        zip_ref.extract(member, ffmpeg_dir)
                        src = os.path.join(ffmpeg_dir, member)
                        shutil.move(src, ffmpeg_path)
                        break
            os.chmod(ffmpeg_path, 0o755)
            os.remove(zip_path)

        else:  # Linux
            url = "https://johnvansickle.com/ffmpeg/releases/ffmpeg-release-amd64-static.tar.xz"
            tar_path = os.path.join(base_path, "ffmpeg.tar.xz")
            urllib.request.urlretrieve(url, tar_path)

            with tarfile.open(tar_path, "r:xz") as tar_ref:
                for member in tar_ref.getmembers():
                    if member.name.endswith("/ffmpeg"):
                        tar_ref.extract(member, ffmpeg_dir)
                        src = os.path.join(ffmpeg_dir, os.path.basename(member.name))
                        shutil.move(src, ffmpeg_path)
                        break
            os.chmod(ffmpeg_path, 0o755)
            os.remove(tar_path)

        if os.path.exists(ffmpeg_path):
            print(f"FFmpeg installed successfully: {ffmpeg_path}")
            return ffmpeg_path
        else:
            raise Exception("FFmpeg install failed.")

    except Exception as e:
        print(f"Error installing FFmpeg: {e}")
        raise Exception("Failed to install FFmpeg. Please install it manually.")


def download_video(url, output_folder):
    """Download YouTube video using yt_dlp with local FFmpeg."""
    ffmpeg_path = check_ffmpeg()

    ydl_opts = {
        "format": "best",
        "outtmpl": os.path.join(output_folder, "%(title)s.%(ext)s"),
        "ffmpeg_location": os.path.dirname(ffmpeg_path),  # point to local ffmpeg/bin
    }

    with YoutubeDL(ydl_opts) as ydl:
        print(f"Downloading video from: {url}")
        ydl.download([url])


def main():
    system = platform.system()
    print(f"YouTube Downloader Starting on {system}...")

    url = input("Enter the YouTube video URL: ").strip()
    if not url:
        print("No URL provided. Exiting.")
        return

    save_path = input("Enter the folder path to save the video or press Enter for default (Downloads folder): ").strip()
    if not save_path:
        save_path = os.path.join(os.path.expanduser("~"), "Downloads")

    print(f"Saving to: {save_path}")

    try:
        download_video(url, save_path)
        print("Download completed successfully!")
    except Exception as e:
        print(f"An error occurred: {e}")

    input("\nPress Enter to exit...")


if __name__ == "__main__":
    main()
