from yt_dlp import YoutubeDL
import os
import sys
import platform
import subprocess
import zipfile
import tarfile
import urllib.request

def get_base_path():
    """Get the base path - works for both script and executable."""
    if getattr(sys, 'frozen', False):
        # Running as compiled executable
        return os.path.dirname(sys.executable)
    else:
        # Running as script
        return os.path.dirname(os.path.abspath(__file__))

def get_ffmpeg_paths():
    """Get platform-specific FFmpeg paths."""
    base_path = get_base_path()
    system = platform.system()
    
    if system == "Windows":
        ffmpeg_dir = os.path.join(base_path, "ffmpeg", "ffmpeg-7.1-essentials_build", "bin")
        ffmpeg_exe = os.path.join(ffmpeg_dir, "ffmpeg.exe")
        return ffmpeg_exe, ffmpeg_dir
    elif system == "Darwin":  # macOS
        ffmpeg_dir = os.path.join(base_path, "ffmpeg", "bin")
        ffmpeg_exe = os.path.join(ffmpeg_dir, "ffmpeg")
        return ffmpeg_exe, ffmpeg_dir
    else:  # Linux
        ffmpeg_dir = os.path.join(base_path, "ffmpeg", "bin")
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
        # Try system FFmpeg first (common on Mac/Linux)
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
        
        # Check again after installation
        if os.path.exists(ffmpeg_exe):
            os.environ["PATH"] = ffmpeg_dir + os.pathsep + os.environ["PATH"]
            print(f"Using FFmpeg from: {ffmpeg_exe}")
            return ffmpeg_exe
        else:
            raise Exception("Failed to install FFmpeg. Please install it manually.")

def install_ffmpeg():
    """Automatically download and install FFmpeg based on the operating system."""
    base_path = get_base_path()
    ffmpeg_exe, ffmpeg_dir = get_ffmpeg_paths()
    
    if os.path.exists(ffmpeg_exe):
        print("FFmpeg is already installed.")
        return
    
    system = platform.system()
    print(f"FFmpeg is missing. Downloading and installing for {system}...")
    
    try:
        if system == "Windows":
            install_ffmpeg_windows(base_path)
        elif system == "Darwin":  # macOS
            install_ffmpeg_mac(base_path)
        else:  # Linux
            install_ffmpeg_linux(base_path)
            
        print("FFmpeg installed successfully.")
    except Exception as e:
        print(f"Error installing FFmpeg: {e}")
        print("\nPlease install FFmpeg manually:")
        if system == "Darwin":
            print("  Run: brew install ffmpeg")
        elif system == "Linux":
            print("  Run: sudo apt install ffmpeg  (Ubuntu/Debian)")
            print("  Or:  sudo yum install ffmpeg  (CentOS/RHEL)")
        else:
            print("  Visit: https://ffmpeg.org/download.html")
        raise

def install_ffmpeg_windows(base_path):
    """Install FFmpeg on Windows."""
    ffmpeg_dir = os.path.join(base_path, "ffmpeg")
    ffmpeg_zip = os.path.join(base_path, "ffmpeg.zip")
    ffmpeg_url = "https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip"
    
    print("Downloading FFmpeg for Windows...")
    subprocess.run(["powershell", "-Command", 
                   f"Invoke-WebRequest -Uri {ffmpeg_url} -OutFile {ffmpeg_zip}"], 
                   check=True)
    
    print("Extracting FFmpeg...")
    with zipfile.ZipFile(ffmpeg_zip, 'r') as zip_ref:
        zip_ref.extractall(ffmpeg_dir)
    
    if os.path.exists(ffmpeg_zip):
        os.remove(ffmpeg_zip)

def install_ffmpeg_mac(base_path):
    """Install FFmpeg on macOS."""
    # Check if Homebrew is available
    try:
        subprocess.run(["brew", "--version"], 
                      capture_output=True, 
                      check=True, 
                      timeout=5)
        print("Installing FFmpeg via Homebrew...")
        subprocess.run(["brew", "install", "ffmpeg"], check=True)
        return
    except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
        pass
    
    # Fallback: Download static build
    print("Downloading FFmpeg static build for macOS...")
    ffmpeg_dir = os.path.join(base_path, "ffmpeg", "bin")
    os.makedirs(ffmpeg_dir, exist_ok=True)
    
    # Download from a static build source
    arch = platform.machine()
    if arch == "arm64":  # Apple Silicon
        ffmpeg_url = "https://evermeet.cx/ffmpeg/ffmpeg-6.1.zip"
    else:  # Intel
        ffmpeg_url = "https://evermeet.cx/ffmpeg/ffmpeg-6.1.zip"
    
    ffmpeg_zip = os.path.join(base_path, "ffmpeg.zip")
    
    print(f"Downloading from {ffmpeg_url}...")
    urllib.request.urlretrieve(ffmpeg_url, ffmpeg_zip)
    
    print("Extracting FFmpeg...")
    with zipfile.ZipFile(ffmpeg_zip, 'r') as zip_ref:
        zip_ref.extractall(ffmpeg_dir)
    
    # Make executable
    ffmpeg_exe = os.path.join(ffmpeg_dir, "ffmpeg")
    if os.path.exists(ffmpeg_exe):
        os.chmod(ffmpeg_exe, 0o755)
    
    if os.path.exists(ffmpeg_zip):
        os.remove(ffmpeg_zip)

def install_ffmpeg_linux(base_path):
    """Install FFmpeg on Linux."""
    print("Attempting to install FFmpeg via package manager...")
    
    # Try apt (Ubuntu/Debian)
    try:
        subprocess.run(["sudo", "apt", "install", "-y", "ffmpeg"], 
                      check=True, 
                      timeout=300)
        return
    except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
        pass
    
    # Try yum (CentOS/RHEL)
    try:
        subprocess.run(["sudo", "yum", "install", "-y", "ffmpeg"], 
                      check=True, 
                      timeout=300)
        return
    except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
        pass
    
    raise Exception("Could not install FFmpeg automatically on Linux")

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
    
    # Keep the window open so the user can see the result
    input("\nPress Enter to exit...")