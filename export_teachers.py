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

# Fetch teachers data
cursor.execute("SELECT * FROM teachers")
teachers = cursor.fetchall()

# Export to CSV
csv_filename = "teachers.csv"
with open(csv_filename, mode='w', newline='', encoding='utf-8') as file:
    writer = csv.writer(file)
    
    # Write header
    writer.writerow([i[0] for i in cursor.description])
    
    # Write data
    writer.writerows(teachers)

print(f"Teachers data exported to {csv_filename} successfully.")

# Close connection
cursor.close()
conn.close()