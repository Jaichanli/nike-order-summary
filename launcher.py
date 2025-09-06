import os
import sys
import subprocess

def resource_path(relative_path):
    """Get absolute path to resource, works for dev and for PyInstaller bundle."""
    try:
        base_path = sys._MEIPASS  # PyInstaller temp folder
    except AttributeError:
        base_path = os.path.dirname(os.path.abspath(sys.executable))
    return os.path.join(base_path, relative_path)

def run_streamlit_app():
    script_path = resource_path("main.py")  # Replace with your actual Streamlit script name
    subprocess.run(["streamlit", "run", script_path])

if __name__ == "__main__":
    run_streamlit_app()
