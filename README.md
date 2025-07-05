# Japan Earthquake Tracker

A full-stack web application that fetches, stores, and displays recent earthquake data from across Japan. This project demonstrates skills in backend development, API integration, and database management. Users can view the 50 most recent earthquakes, filter the results by prefecture, and sort the data by time or magnitude.

## Features

* **Live Data:** Fetches real-time earthquake data from the official Japan Meteorological Agency (JMA) public API.
* **Reverse Geocoding:** Converts earthquake latitude and longitude coordinates into human-readable city and prefecture names using the OpenStreetMap Nominatim API.
* **Persistent Storage:** Stores and manages earthquake data in a local SQLite database, preventing duplicate entries.
* **Interactive Frontend:** Allows users to filter the earthquake list by prefecture and sort the data by clicking on table headers.
* **Visual Subscription Form:** Includes a UI for a mock user subscription service for major quake notifications.

## Technologies Used

* **Backend:** Python, Flask, SQLite3
* **Frontend:** HTML, CSS, Jinja2 Templating
* **APIs & Libraries:** Requests (for API calls), JMA Earthquake API, OpenStreetMap Nominatim API

## How It Works

1.  **Data Collection (`update_database.py`):** A Python script runs to fetch the latest earthquake list from the JMA API. For each new earthquake, it makes a second API call to a reverse geocoding service to get the English city and prefecture names from its coordinates. This cleaned and enriched data is then saved into an SQLite database.
2.  **Backend (`app.py`):** A Flask web server reads the data from the `earthquakes.db` file. It handles user requests for filtering (by prefecture) and sorting (by magnitude, time, etc.) by building dynamic SQL queries. It then passes the queried data to the frontend.
3.  **Frontend (`index.html`):** A single HTML page built with the Jinja2 templating engine displays the data. It dynamically creates the table of earthquakes and populates the filter dropdown menu based on the data provided by the Flask backend.

## Setup and Installation

To run this project on your local machine, follow these steps:

1.  **Clone the repository:**
    ```sh
    git clone [https://github.com/ashleywyattjapan/earthquakeTracker.git](https://github.com/ashleywyattjapan/earthquakeTracker.git)
    cd earthquakeTracker
    ```

2.  **Set up a virtual environment (recommended):**
    ```sh
    python3 -m venv venv
    source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
    ```

3.  **Install the required libraries:**
    ```sh
    pip install Flask requests
    ```

4.  **Create and Populate the Database:**
    Run the update script once to create the `earthquakes.db` file and fill it with the latest data. This may take a few minutes as it makes many API calls.
    ```sh
    python3 update_database.py
    ```

5.  **Run the Flask Application:**
    ```sh
    python3 app.py
    ```

6.  Open your web browser and navigate to `http://127.0.0.1:5000/`.

