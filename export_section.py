import mysql.connector
import csv

# Connect to MySQL
conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    database="class_scheduler",
    charset="utf8mb4",
    collation="utf8mb4_general_ci"
)

cursor = conn.cursor()

# Fetch all data from the sections table
cursor.execute("SELECT * FROM sections")
sections = cursor.fetchall()

# Get column names
column_names = [i[0] for i in cursor.description]

# Export to CSV
filename = "sections_export.csv"
with open(filename, mode="w", newline="", encoding="utf-8") as file:
    writer = csv.writer(file)
    writer.writerow(column_names)  # Write header
    writer.writerows(sections)  # Write data rows

print(f"✅ Data from 'sections' table exported successfully to {filename}")

# Close the connection
cursor.close()
conn.close()
