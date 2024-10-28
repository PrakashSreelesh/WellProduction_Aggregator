# WellProduction_Aggregator

**WellProduction_Aggregator** is a Python-based application that aggregates well production data and serves it via a REST API. The application stores data in an SQLite database, providing easy access to annual oil, gas, and brine production data by well.

## Features

- Aggregates well production data from various sources.
- Stores data in a lightweight SQLite database.
- Provides a RESTful API for easy access to production data.

## Installation

1. Install Required Packages:
   # pip install -r requirements.txt

2. Running the Project:
   # python main.py
    - The API will be available at http://localhost:8080.

## API Endpoints

1. Get Annual Production Data for a Specific Well
    - To retrieve the annual production data for a specific well, use the following endpoint:
    GET http://localhost:8080/data?well=34059242540000

    - Example Response:
    {
        "oil": 381,
        "gas": 108074,
        "brine": 939
    }

2. Get All Annual Production Data
    - To retrieve the list of all annual production data from the database, use the following endpoint:
    GET http://localhost:8080/data/all

    - Example Response:
    [
        {
            "api_well_number": "34013205830000",
            "brine": 0,
            "gas": 0,
            "oil": 0,
            "production_year": 2020
        },
        {
            "api_well_number": "34013206190000",
            "brine": 0,
            "gas": 0,
            "oil": 0,
            "production_year": 2020
        },
        ...
    ]


