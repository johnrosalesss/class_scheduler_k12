from flask import Flask, render_template, request, jsonify
from datetime import timedelta
import mysql.connector
import pandas as pd

app = Flask(__name__)

def get_schedule(filter_by=""):
    conn = mysql.connector.connect(host="localhost", user="root", password="", database="class_scheduler")
    cursor = conn.cursor(dictionary=True)  # Fetch results as dictionaries
    
    query = "SELECT * FROM schedule"
    if filter_by:
        query += " WHERE day = %s OR teacher_name = %s"
        cursor.execute(query, (filter_by, filter_by))
    else:
        cursor.execute(query)
    
    data = cursor.fetchall()
    conn.close()
    
    # Handle empty results
    if not data:
        return pd.DataFrame()

    return pd.DataFrame(data)

@app.route('/', methods=['GET', 'POST'])
def index():
    filter_by = request.form.get("filter", "")
    schedule_df = get_schedule(filter_by)

    return render_template("index.html", 
                           tables=[schedule_df.to_html(classes="data", index=False)] if not schedule_df.empty else [],
                           filter_by=filter_by)

@app.route('/get_schedule', methods=['GET'])
def get_schedule_json():
    conn = mysql.connector.connect(host="localhost", user="root", password="", database="class_scheduler")
    cursor = conn.cursor(dictionary=True)  # Fetch as dictionary

    # Fetch column names and schedule data
    cursor.execute("SELECT * FROM schedule")
    data = cursor.fetchall()
    conn.close()

    # Handle empty result
    if not data:
        return jsonify({"columns": [], "data": []})

    # Get column names from the first row
    columns = list(data[0].keys())

    # Convert timedelta objects (TIME columns) to strings
    for row in data:
        for key, value in row.items():
            if isinstance(value, timedelta):
                row[key] = str(value)

    return jsonify({"columns": columns, "data": data})

if __name__ == '__main__':
    app.run(debug=True)
