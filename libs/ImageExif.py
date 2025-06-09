import math
import os
import sqlite3
from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS


from singleton_decorator import singleton
@singleton
class ImageExif:
    def __init__(self):
        pass
        

    def get_exif_data(self, image_path:str):
        """Extract EXIF data from an image."""
        try:
            image = Image.open(image_path)
            exif_data = image._getexif()
            if exif_data is None:
                return None
            exif = {
                TAGS.get(tag, tag): value
                for tag, value in exif_data.items()
                if tag in TAGS
            }
            return exif
        except Exception as e:
            print(f"Error extracting EXIF data: {e}")
            return None

    def get_gps_info(self, exif_data):
        """Extract GPS information from EXIF data."""
        if not exif_data:
            return None
        gps_info = {}
        for key, value in exif_data.items():
            if key == "GPSInfo":
                gps_info = {
                    GPSTAGS.get(tag, tag): value[tag]
                    for tag in value
                    if tag in GPSTAGS
                }
        return gps_info

    def convert_to_degrees(self, value):
        """Convert GPS coordinates to degrees."""
        d, m, s = value
        return d + (m / 60.0) + (s / 3600.0)

    def get_location(self, gps_info):
        """Extract location data from GPS info."""
        if not gps_info:
            return None
        lat = gps_info.get("GPSLatitude")
        lat_ref = gps_info.get("GPSLatitudeRef")
        lon = gps_info.get("GPSLongitude")
        lon_ref = gps_info.get("GPSLongitudeRef")

        if lat and lat_ref and lon and lon_ref:
            lat = self.convert_to_degrees(lat)
            if lat_ref != "N":
                lat = -lat
            lon = self.convert_to_degrees(lon)
            if lon_ref != "E":
                lon = -lon
            return (lat, lon)
        return None

    def get_date_taken(self,exif_data):
        """Extract date taken from EXIF data."""
        if not exif_data:
            return None
        return exif_data.get("DateTimeOriginal")


    def gps_to_city(self,location):
        if location is None:
            return None
        # TODO: use config
        db_path = f"/app/data/geo_names.db"
        query = """
            SELECT
                c.id,
                c.name,
                c.label,
                c.latitude,
                c.longitude,
                SQRT(POWER((c.latitude - ?), 2) + POWER((c.longitude -  ?), 2)) AS distance
            FROM
                cities c
            ORDER BY
                distance ASC
            LIMIT 1;
        """
        conn = None
 
        conn = sqlite3.connect(db_path)
        conn.create_function("SQRT", 1, math.sqrt)
        conn.create_function("POWER", 2, lambda x, y: math.pow(x, y))
        # Connect to the SQLite database
        conn.row_factory = sqlite3.Row  # This enables fetching rows as dictionaries
        cursor = conn.cursor()
        cursor.execute(query, location)
    
        # Fetch one row as a dictionary
        row = cursor.fetchone()
        # Close the connection
        conn.close()


        # Convert the row to a dictionary
        if row:
            return dict(row)
        return None

   


    def parse(self, image_path):
        exif_data = self.get_exif_data(image_path)
        if exif_data is None:
            return None
        gps_info = self.get_gps_info(exif_data)
        location = self.get_location(gps_info)
        city = self.gps_to_city(location)
        date_taken = self.get_date_taken(exif_data)
        
        return {
            "location": location,
            "date_taken": date_taken,
            "city": city
        }