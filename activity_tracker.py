#!/usr/bin/env python3
from flask import Flask, request, render_template, redirect, url_for, jsonify
import sqlite3
from datetime import date, timedelta, datetime

app = Flask(__name__)

# Initialize database
def init_db():
    conn = sqlite3.connect('database/tracker.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS activities (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date DATE NOT NULL,
            distance REAL NOT NULL,
            average_pace TEXT NOT NULL,
            fastest_mile_time TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

# Home route: Log activity form
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # Get form data
        activity_date = request.form.get('date')
        distance = request.form.get('distance')
        average_pace = request.form.get('average_pace')
        fastest_mile_time = request.form.get('fastest_mile_time')

        # Validate inputs
        if not activity_date or not distance or not average_pace or not fastest_mile_time:
            return "All fields are required.", 400
        
        # Save data to database
        conn = sqlite3.connect('database/tracker.db')
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO activities (date, distance, average_pace, fastest_mile_time)
            VALUES (?, ?, ?, ?)
        ''', (activity_date, float(distance), average_pace, fastest_mile_time))
        conn.commit()
        conn.close()

        return redirect(url_for('index'))

    return render_template('index.html')

# Activities route: Display all logged activities
@app.route('/activities')
def activities():
    conn = sqlite3.connect('database/tracker.db')
    cursor = conn.cursor()
    
    # Query all logged activities
    cursor.execute("SELECT id, date, distance, average_pace, fastest_mile_time FROM activities ORDER BY date DESC")
    rows = cursor.fetchall()
    
    # Calculate the total distance
    cursor.execute("SELECT SUM(distance) FROM activities")
    total_distance = cursor.fetchone()[0] or 0  # Default to 0 if no activities
    
    conn.close()

    # Render the template with activities and total distance
    return render_template('activities.html', activities=rows, total_distance=total_distance)

# API route for D3.js heatmap data
@app.route('/api/calendar-heatmap')
def calendar_heatmap():
    conn = sqlite3.connect('database/tracker.db')
    cursor = conn.cursor()
    cursor.execute("SELECT date, distance FROM activities")
    rows = cursor.fetchall()
    conn.close()

    # Format data for D3.js
    heatmap_data = [
        {"date": datetime.strptime(row[0], '%Y-%m-%d').strftime('%Y-%m-%d'), "value": row[1]}
        for row in rows
    ]
    print("Heatmap Data:", heatmap_data)  # Debugging backend data
    return jsonify(heatmap_data)

@app.route('/api/progress-data')
def progress_data():

    # Calculate total mileage logged so far
    conn = sqlite3.connect('database/tracker.db')
    cursor = conn.cursor()
    cursor.execute("SELECT SUM(distance) FROM activities")
    total_mileage = cursor.fetchone()[0] or 0  # Default to 0 if no data
    conn.close()

    # Calculate the goal pace
    today = date.today()
    day_of_year = today.timetuple().tm_yday
    goal_pace = (1000 / 365) * day_of_year  # 1000 miles divided by 365 days

    return jsonify({
        "total_mileage": total_mileage,
        "goal_pace": goal_pace
    })


# Initialize database and run the app
if __name__ == '__main__':
    init_db()
    app.run(debug=True, port=5001)
