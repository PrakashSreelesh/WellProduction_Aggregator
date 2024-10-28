from flask import jsonify, request
import pandas as pd
import sqlite3
import os

class ProductionDataProcessor:
    def __init__(self, excel_file, db_file="annual_production.db"):
        self.excel_file = excel_file
        self.db_file = db_file

    def process_and_create_db(self):
        print("DB Creation: Start")
        # Check if the database already exists to avoid recreating it
        if os.path.exists(self.db_file):
            print(f"Database '{self.db_file}' already exists. No action taken.")
            return

        # Load the Excel data and normalize column names
        data = pd.read_excel(self.excel_file)
        data.columns = data.columns.str.strip()  # Remove extra spaces in column names
        # print(data)

        # Aggregate annual data by summing quarterly values
        annual_data = data.groupby(['API WELL  NUMBER', 'Production Year']).agg({
            'OIL': 'sum',
            'GAS': 'sum',
            'BRINE': 'sum'
        }).reset_index()

        # print("Aggregated Annual Data:\n", annual_data)

        # Convert to the desired tuple format
        data_tuples = [
            (str(row['API WELL  NUMBER']), int(row['Production Year']), int(row['OIL']), int(row['GAS']), int(row['BRINE']))
            for _, row in annual_data.iterrows()
        ]
        
        # print("Converted Data Tuples:\n", data_tuples)

        # Connect to SQLite DB, creating it if it doesn't exist
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()

        # Updated CREATE TABLE statement with accurate data types
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



def initialize_routes(app):
    '''
    API route to get the annual production data for a specific well
    '''
    @app.route('/data', methods=['GET'])
    def get_annual_data():
        well_number = request.args.get('well')
        if not well_number:
            return jsonify({"error": "API WELL NUMBER not provided"}), 400

        # Connect to the SQLite database
        conn = sqlite3.connect("annual_production.db")
        cursor = conn.cursor()

        # Query for the well number's annual data
        cursor.execute('''
            SELECT oil, gas, brine FROM production_data
            WHERE api_well_number = ?
        ''', (well_number,))

        row = cursor.fetchone()
        conn.close()

        if row:
            print("row: ",row)
            result = {
                "oil": row[0],
                "gas": row[1],
                "brine": row[2]
            }
            return jsonify(result)
        else:
            return jsonify({"error": "Data not found for the given API WELL NUMBER"}), 404


    '''
    API route to get all the annual production data from the database table production_data
    '''
    @app.route('/data/all', methods=['GET'])
    def get_all_data():
        conn = sqlite3.connect("annual_production.db")
        cursor = conn.cursor()

        cursor.execute('SELECT * FROM production_data')
        rows = cursor.fetchall()
        conn.close()

        if rows:
            print(rows)

            result = [
                {
                    "api_well_number": row[0],
                    "production_year": row[1],
                    "oil": row[2],
                    "gas": row[3],
                    "brine": row[4]
                }
                for row in rows
            ]

            return jsonify(result), 200
        else:
            return jsonify({"message": "No data found"}), 404