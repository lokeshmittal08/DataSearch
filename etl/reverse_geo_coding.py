import sqlite3
import csv
from dotenv import load_dotenv
import os

import pandas as pd


load_dotenv()

base_dir = os.getenv('BASE_DIR')


cities_df = pd.read_csv(f'/app/etl/geonames-all-cities-with-a-population-1000.csv',delimiter=';')
# dd(cities_df.head())

conn = sqlite3.connect(f"/app/data/geo_names.db")
cur = conn.cursor()

# Create table
cur.execute("DROP TABLE IF EXISTS cities;")
cur.execute("""
    CREATE TABLE cities (
        id INTEGER PRIMARY KEY,
        name TEXT,
        label TEXT,
        latitude REAL,
        longitude REAL
    );
""")

# Read and insert CSV data

for index, row in cities_df.iterrows():
    sql = "INSERT INTO cities (id, name, label, latitude, longitude) VALUES (?, ?, ?, ?, ?);"
    geo =  tuple(map(float,  row['Coordinates'].split(',')))
    data = (row['Geoname ID'], row['ASCII Name'], row['Country name EN'],geo[0], geo[1])
    cur.execute(sql, data)
conn.commit()
conn.close()