import os
import pandas as pd
import sqlite3

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
        
        print("Aggrigated Annual Data: \n",annual_data.head())

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

if __name__ == "__main__":
    # app = create_app()

    media_dir = os.path.join(os.path.dirname(__file__), 'media')
    report_file = os.path.join(media_dir, '20210309_2020_1 - 4 (1) (1) (1) (1).xls')
    
    # Process the production data 
    processor = ProductionDataProcessor(report_file)
    processor.process_and_create_db()

    # app.run(debug=True)
