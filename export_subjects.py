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

# Fetch subjects from the database
cursor.execute("SELECT * FROM subjects")
subjects = cursor.fetchall()

# Define the CSV file name
filename = "subjects.csv"

# Export to CSV
with open(filename, mode='w', newline='', encoding='utf-8') as file:
    writer = csv.writer(file)
    
    # Write the header (adjust column names as needed)
    writer.writerow(['Subject Code', 'Subject Name', 'Program', 'Year Level', 'Hours Per Week', 'Semester'])
    
    # Write the data
    for subject in subjects:
        writer.writerow(subject)

print(f"Subjects exported to {filename} successfully!")

# Close the database connection
cursor.close()
conn.close()
