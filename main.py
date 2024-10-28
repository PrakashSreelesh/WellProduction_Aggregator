import os
import subprocess
import sys
import pandas as pd
import sqlite3
from app import create_app
from app.routes import ProductionDataProcessor


def main():
    media_dir = os.path.join(os.path.dirname(__file__), 'media')
    report_file = os.path.join(media_dir, '20210309_2020_1 - 4 (1) (1) (1) (1).xls')

    processor = ProductionDataProcessor(report_file)
    processor.process_and_create_db()



if __name__ == "__main__":
    app = create_app()
    
    main()

    app.run(port=8080)
