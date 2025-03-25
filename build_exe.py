import os
import subprocess
import sys


def install_pyinstaller():
    """Ensure PyInstaller is installed."""
    try:
        import PyInstaller
    except ImportError:
        print("PyInstaller not found. Installing...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])


def build_executable():
    """Run PyInstaller to create an executable from the src/ folder."""
    install_pyinstaller()
    script_path = os.path.join("src", "main.py")
    if not os.path.exists(script_path):
        print(
            f"Error: {script_path} not found. Make sure your script is named 'main.py' inside src/."
        )
        return

    print(f"Building executable for {script_path}...")
    subprocess.run(
        [
            "pyinstaller",
            "--onefile",
            "--windowed",
            "--name",
            "AudioMixer.exe",
            "--icon",
            "icon.ico",
            "--add-data",
            "icon.ico:.",
            script_path,
        ]
    )
    print("Build complete! Check the 'dist' folder for the executable.")


if __name__ == "__main__":
    build_executable()
