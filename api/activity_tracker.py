from flask import Flask, request, render_template, redirect, url_for, jsonify
import sqlite3
import os
from datetime import date

app = Flask(__name__, template_folder="../templates")  # Ensure Flask finds the HTML templates

DATABASE_PATH = os.path.join(os.path.dirname(__file__), "../database/tracker.db")

# Initialize database (ensure it exists)
def init_db():
    os.makedirs(os.path.dirname(DATABASE_PATH), exist_ok=True)
    conn = sqlite3.connect(DATABASE_PATH)
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

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/activities')
def activities():
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT id, date, distance, average_pace, fastest_mile_time FROM activities ORDER BY date DESC")
    rows = cursor.fetchall()
    conn.close()
    return render_template('activities.html', activities=rows)

@app.route('/api/progress-data')
def progress_data():
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT SUM(distance) FROM activities")
    total_mileage = cursor.fetchone()[0] or 0
    conn.close()

    today = date.today()
    day_of_year = today.timetuple().tm_yday
    goal_pace = (1000 / 365) * day_of_year  

    return jsonify({"total_mileage": total_mileage, "goal_pace": goal_pace})

@app.route('/api/calendar-heatmap')
def calendar_heatmap():
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT date, distance FROM activities")
    rows = cursor.fetchall()
    conn.close()

    heatmap_data = [{"date": row[0], "value": row[1]} for row in rows]
    return jsonify(heatmap_data)



if __name__ == '__main__':
    init_db()  # Ensure the database is initialized
    port = int(os.environ.get("PORT", 5000))  # Get Vercel's assigned port
    app.run(host='0.0.0.0', port=port)
