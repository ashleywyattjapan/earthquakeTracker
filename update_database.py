import requests
import json
import sqlite3
import time

# --- 1. Define Constants ---
QUAKE_API_URL = "https://www.jma.go.jp/bosai/quake/data/list.json"
GEOCODE_API_URL = "https://nominatim.openstreetmap.org/reverse"
DB_FILE = "earthquakes.db"

# --- 2. Function to Get Location from Coordinates ---
def get_location_from_coords(lat, lon):
    """Takes latitude and longitude and returns the city and prefecture in English."""
    try:
        params = {
            'format': 'json',
            'lat': lat,
            'lon': lon,
            'accept-language': 'en' # Request English names
        }
        headers = {
            'User-Agent': 'JapanQuakeTracker/1.0 (Portfolio Project)'
        }
        response = requests.get(GEOCODE_API_URL, params=params, headers=headers)
        response.raise_for_status()
        location_data = response.json()
        
        address = location_data.get('address', {})
        city = address.get('city', address.get('town', address.get('village', 'N/A')))
        prefecture = address.get('state', address.get('province', 'N/A'))
        
        return city, prefecture
    except requests.exceptions.RequestException as e:
        print(f"  - Geocoding API Error: {e}")
        return 'N/A', 'N/A'
    except json.JSONDecodeError:
        print("  - Geocoding API Error: Failed to decode JSON response.")
        return 'N/A', 'N/A'

# --- 3. Function to Set Up the Database ---
def setup_database():
    """Creates the database and table with new city/prefecture columns."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS earthquakes(
            event_id TEXT PRIMARY KEY,
            time TEXT,
            epicenter_name TEXT,
            magnitude REAL,
            latitude REAL,
            longitude REAL,
            city TEXT,
            prefecture TEXT
        )
    ''')
    conn.commit()
    conn.close()
    print(f"Database '{DB_FILE}' is set up with location columns.")

# --- 4. Function to Fetch and Save Data ---
def fetch_and_save_data():
    """Fetches quake data, gets location names, and saves to the database."""
    print("Fetching latest earthquake data...")
    try:
        response = requests.get(QUAKE_API_URL)
        response.raise_for_status()
        earthquakes = response.json()
        
        print(f"API call successful. Found {len(earthquakes)} total items in the feed.")
        if not isinstance(earthquakes, list):
            print("Error: API data is not a list. Aborting.")
            return

        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()

        new_quakes_count = 0
        for quake in earthquakes:
            event_id = quake.get('eid')
            if not event_id:
                continue

            time_str = quake.get('at')
            # Use the English epicenter name provided by the JMA API
            epicenter_name = quake.get('en_anm', quake.get('anm')) # Fallback to Japanese if English isn't there
            magnitude = quake.get('mag')
            coord_str = quake.get('cod', '')

            try:
                lat_str = coord_str.split('+')[1]
                lon_str = coord_str.split('+')[2].split('-')[0]
                latitude = float(lat_str)
                longitude = float(lon_str)
            except (IndexError, ValueError):
                continue

            if not all([time_str, epicenter_name, magnitude]):
                continue

            print(f"Processing event {event_id}...")
            city, prefecture = get_location_from_coords(latitude, longitude)
            
            cursor.execute('''
                INSERT OR IGNORE INTO earthquakes (event_id, time, epicenter_name, magnitude, latitude, longitude, city, prefecture)
                VALUES (?,?,?,?,?,?,?,?)
            ''', (event_id, time_str, epicenter_name, magnitude, latitude, longitude, city, prefecture))
            
            if cursor.rowcount > 0:
                new_quakes_count += 1
            
            time.sleep(1) 

        conn.commit()
        conn.close()
        print(f"Process complete. Added {new_quakes_count} new earthquake(s) to the database.")

    except requests.exceptions.RequestException as e:
        print(f"Error fetching data: {e}")
    except sqlite3.Error as e:
        print(f"Database error: {e}")
    except json.JSONDecodeError:
        print("Error: Failed to decode JSON from the API response.")
        print("Response text:", response.text)

# --- 5. Main Execution Block ---
if __name__ == "__main__":
    setup_database()
    fetch_and_save_data()
