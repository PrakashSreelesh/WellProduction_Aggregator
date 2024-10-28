import os
import subprocess
import sys
import pandas as pd
import sqlite3
from app import create_app
from app.routes import ProductionDataProcessor

def install_requirements():
    """Install required packages from requirements.txt."""
    print("Installing dependencies from requirements.txt")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("Requirements installed successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Error occurred while installing requirements: {e}")
        sys.exit(1)

def main():
    media_dir = os.path.join(os.path.dirname(__file__), 'media')
    report_file = os.path.join(media_dir, '20210309_2020_1 - 4 (1) (1) (1) (1).xls')

    processor = ProductionDataProcessor(report_file)
    processor.process_and_create_db()



if __name__ == "__main__":
    install_requirements()

    app = create_app()
    main()

    app.run(port=8080)
