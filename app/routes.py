from flask import jsonify, request
import pandas as pd
import sqlite3
import os

class ProductionDataProcessor:
    def __init__(self, excel_file, db_file="annual_production.db"):
        self.excel_file = excel_file
        self.db_file = db_file

    def process_and_create_db(self):
        if os.path.exists(self.db_file):
            print(f"Database '{self.db_file}' already exists. No action taken.")
            return

        data = pd.read_excel(self.excel_file)

        # Group by 'API WELL NUMBER' & 'Production Year' then sum quarterly data
        annual_data = data.groupby(['API WELL  NUMBER', 'Production Year']).agg({
            'OIL': 'sum',
            'GAS': 'sum',
            'BRINE': 'sum'
        }).reset_index()
        
        print("Aggrigated Annual Data: \n",annual_data)

        # db connect: will create it, if db not exist
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS production_data (
                api_well_number TEXT,
                production_year INTEGER,
                oil INTEGER,
                gas INTEGER,
                brine INTEGER
            )
        ''')
        conn.commit()

        # Insert aggregated data in database
        for _, row in annual_data.iterrows():
            cursor.execute('''
                INSERT INTO production_data (api_well_number, production_year, oil, gas, brine)
                VALUES (?, ?, ?, ?, ?)
            ''', (row['API WELL  NUMBER'], row['Production Year'], row['OIL'], row['GAS'], row['BRINE']))

        conn.commit()
        conn.close()

        print(f"Database '{self.db_file}' created and data inserted successfully.")



def initialize_routes(app):
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
            result = {
                "oil": row[0],
                "gas": row[1],
                "brine": row[2]
            }
            return jsonify(result)
        else:
            return jsonify({"error": "Data not found for the given API WELL NUMBER"}), 404

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