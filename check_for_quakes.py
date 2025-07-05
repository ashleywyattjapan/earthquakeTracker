import requests
import time
from datetime import datetime, timedelta, timezone

# --- User Settings ---
# Users can change these values to match their preferences
MY_PREFECTURE = "Hyogo"  # The prefecture to monitor
MAGNITUDE_THRESHOLD = 5.0 # The minimum magnitude to trigger an alert
CHECK_INTERVAL_SECONDS = 300 # Check every 5 minutes

# We need this function again, so we include it here
def get_location_from_coords(lat, lon):
    """Takes latitude and longitude and returns the city and prefecture in English."""
    try:
        params = {'format': 'json', 'lat': lat, 'lon': lon, 'accept-language': 'en'}
        headers = {'User-Agent': 'JapanQuakeTracker/1.0 (Notification Script)'}
        response = requests.get("https://nominatim.openstreetmap.org/reverse", params=params, headers=headers)
        response.raise_for_status()
        address = response.json().get('address', {})
        return address.get('state', address.get('province', 'N/A'))
    except Exception:
        return 'N/A'

def check_for_major_quakes():
    """Fetches the latest quake data and prints an alert if conditions are met."""
    print(f"Checking for earthquakes in {MY_PREFECTURE} with magnitude >= {MAGNITUDE_THRESHOLD}...")
    try:
        response = requests.get("https://www.jma.go.jp/bosai/quake/data/list.json")
        response.raise_for_status()
        earthquakes = response.json()

        # We only want to check very recent earthquakes
        now = datetime.now(timezone.utc)
        time_limit = now - timedelta(minutes=10)

        for quake in earthquakes:
            quake_time_str = quake.get('at')
            if not quake_time_str:
                continue
            
            # Convert quake time string to a comparable datetime object
            quake_time = datetime.fromisoformat(quake_time_str)

            # Check if the quake is recent and if its magnitude is high enough
            if quake_time > time_limit and float(quake.get('mag', 0)) >= MAGNITUDE_THRESHOLD:
                latitude = quake.get('hypo', {}).get('lat')
                longitude = quake.get('hypo', {}).get('lon')

                if not latitude or not longitude:
                    continue

                # Get the prefecture for this major quake
                prefecture = get_location_from_coords(latitude, longitude)
                
                # If the prefecture matches the user's setting, print an alert
                if prefecture == MY_PREFECTURE:
                    print("\n" + "="*40)
                    print("!!! MAJOR EARTHQUAKE ALERT !!!")
                    print(f"  Time: {quake_time_str}")
                    print(f"  Location: {quake.get('en_anm')}, {prefecture}")
                    print(f"  Magnitude: {quake.get('mag')}")
                    print("="*40 + "\n")
                
                time.sleep(1) # Be polite to the geocoding API

    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    print("Starting earthquake notification monitor...")
    while True:
        check_for_major_quakes()
        time.sleep(CHECK_INTERVAL_SECONDS)
