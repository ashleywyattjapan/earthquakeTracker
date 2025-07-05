import sqlite3
from flask import Flask, render_template, request, flash, redirect, url_for

# --- 1. Initialize the Flask App and Configure the Database ---
app = Flask(__name__)
app.config['SECRET_KEY'] = 'a_super_secret_key_for_flashing_messages'
DB_FILE = "earthquakes.db"

# --- 2. Function to Get Data from the Database ---
def get_db_connection():
    """Creates a connection to the SQLite database."""
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn

# --- 3. Define the Main Route ---
@app.route('/')
def index():
    """Handles displaying the main page with filters and sorting."""
    # Get filter and sort parameters from the URL
    selected_prefecture = request.args.get('prefecture')
    sort_by = request.args.get('sort_by', 'time') # Default sort is by time
    order = request.args.get('order', 'desc') # Default order is descending

    # --- Validate sort parameters to prevent errors ---
    allowed_sort_columns = ['time', 'epicenter_name', 'magnitude', 'city', 'prefecture']
    if sort_by not in allowed_sort_columns:
        sort_by = 'time'
    if order not in ['asc', 'desc']:
        order = 'desc'

    conn = get_db_connection()
    prefectures = conn.execute("SELECT DISTINCT prefecture FROM earthquakes WHERE prefecture != 'N/A' ORDER BY prefecture").fetchall()

    # Build the base SQL query
    query = 'SELECT * FROM earthquakes'
    params = []

    if selected_prefecture and selected_prefecture != 'all':
        query += ' WHERE prefecture = ?'
        params.append(selected_prefecture)
    
    # Add the dynamic ORDER BY clause
    query += f' ORDER BY {sort_by} {order.upper()}'
    
    query += ' LIMIT 50'
    
    earthquakes = conn.execute(query, params).fetchall()
    conn.close()
    
    # Render the HTML, passing all the necessary data to the template
    return render_template('index.html', 
                           earthquakes=earthquakes, 
                           prefectures=prefectures, 
                           selected_prefecture=selected_prefecture,
                           sort_by=sort_by,
                           order=order)

# --- 4. "Visual-Only" Subscription Route ---
@app.route('/subscribe', methods=['POST'])
def subscribe():
    """Handles the form submission for notification sign-ups."""
    flash('Thank you for subscribing!', 'success')
    return redirect(url_for('index'))

# --- 5. Run the App ---
if __name__ == '__main__':
    app.run(debug=True)
