from flask import Flask, jsonify, request
import sqlite3

app = Flask(__name__)

@app.route('/data', methods=['GET'])
def get_annual_data():
    well_number = request.args.get('well')
    if not well_number:
        return jsonify({"error": "API WELL NUMBER not provided"}), 400

    print(type(well_number))

    # Connect to the SQLite database
    conn = sqlite3.connect("annual_production.db")
    cursor = conn.cursor()

    # Query the database
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



if __name__ == '__main__':
    app.run(port=8080)
