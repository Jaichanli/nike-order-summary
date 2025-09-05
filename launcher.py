import subprocess
import sys
import os

def resource_path(relative_path: str) -> str:
    """ Get absolute path to resource, works for dev and for PyInstaller """
    if hasattr(sys, "_MEIPASS"):  # PyInstaller sets this
        base_path = sys._MEIPASS
    else:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

def main():
    app_path = resource_path("app.py")
    cmd = [sys.executable, "-m", "streamlit", "run", app_path, "--server.port", "8501"]
    subprocess.run(cmd)

if __name__ == "__main__":
    main()
