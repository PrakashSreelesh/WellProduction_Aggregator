import os
import pandas as pd
import sqlite3
from flask import Flask, jsonify, request

app = Flask(__name__)

class ProductionDataProcessor:
    def __init__(self, excel_file, db_file="annual_production.db"):
        self.excel_file = excel_file
        self.db_file = db_file

    def process_and_create_db(self):
        print("DB Creation: Start")

        if os.path.exists(self.db_file):
            print(f"Database '{self.db_file}' already exists. No action taken.")
            return

        data = pd.read_excel(self.excel_file)
        data.columns = data.columns.str.strip()
        print(data)

        # Aggregate annual data
        annual_data = data.groupby(['API WELL  NUMBER', 'Production Year']).agg({
            'OIL': 'sum',
            'GAS': 'sum',
            'BRINE': 'sum'
        }).reset_index()

        print("Aggregated Annual Data:\n", annual_data)

        # Convert to the tuple format
        data_tuples = [
            (str(row['API WELL  NUMBER']), int(row['Production Year']), int(row['OIL']), int(row['GAS']), int(row['BRINE']))
            for _, row in annual_data.iterrows()
        ]
        
        print("Converted Data Tuples:\n", data_tuples)

        # Connect to SQLite DB, creating it if it doesn't exist
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS production_data (
                api_well_number TEXT PRIMARY KEY,  -- Storing as TEXT to handle large numbers
                production_year INTEGER,
                oil INTEGER DEFAULT 0,
                gas INTEGER DEFAULT 0,
                brine INTEGER DEFAULT 0
            )
        ''')
        conn.commit()

        # Insert cleaned data into the database using the tuple format
        for data_tuple in data_tuples:
            cursor.execute('''
                INSERT OR REPLACE INTO production_data (api_well_number, production_year, oil, gas, brine)
                VALUES (?, ?, ?, ?, ?)
            ''', data_tuple)

        conn.commit()
        conn.close()

        print(f"Database '{self.db_file}' created and data inserted successfully.")

# Define a route to get the annual production data for a specific well
@app.route('/data', methods=['GET'])
def get_annual_data():
    well_number = request.args.get('well')
    if not well_number:
        return jsonify({"error": "API WELL NUMBER not provided"}), 400

    conn = sqlite3.connect("annual_production.db")
    cursor = conn.cursor()

    cursor.execute('''
        SELECT oil, gas, brine FROM production_data
        WHERE api_well_number = ?
    ''', (well_number,))

    row = cursor.fetchone()
    conn.close()

    if row:
        print("row: ",row)
        # print("row list: ",list(row))
        result = {
            "oil": row[0],
            "gas": row[1],
            "brine": row[2]
        }
        return jsonify(result)
    else:
        return jsonify({"error": "Data not found for the given API WELL NUMBER"}), 404

if __name__ == "__main__":
    media_dir = os.path.join(os.path.dirname(__file__), 'media')
    report_file = os.path.join(media_dir, '20210309_2020_1 - 4 (1) (1) (1) (1).xls')

    processor = ProductionDataProcessor(report_file)
    processor.process_and_create_db()

    app.run(port=8080)
