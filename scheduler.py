import mysql.connector
import random
import csv

# Debug message
print("Connecting to MySQL...")

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
print("Connected successfully!")

# Load data from tables
print("Loading subjects...")
cursor.execute("SELECT * FROM subjects")
subjects = cursor.fetchall()

print("Loading teacher_subjects...")
cursor.execute("SELECT * FROM teacher_subjects")
teacher_subjects = cursor.fetchall()

print("Loading rooms...")
cursor.execute("SELECT * FROM rooms")
rooms = cursor.fetchall()

print("Loading time slots...")
cursor.execute("SELECT * FROM time_slots")
time_slots = cursor.fetchall()

# Clear old schedule
print("Clearing old schedule...")
cursor.execute("DELETE FROM schedule")

# Prepare to track assigned slots and unassigned subjects
assigned_slots = set()
unassigned_subjects = []

# Schedule each subject for 3 hours a week
for subject in subjects:
    subject_code, subject_name, program, year_level, lecture_hours = subject  # Ignore subject_name

    available_teacher_subjects = [t for t in teacher_subjects if t[2] == subject_code]
    if not available_teacher_subjects:
        print(f"⚠ No teacher available for {subject_code}, skipping...")
        unassigned_subjects.append((subject_code, "No available teacher"))
        continue

    # Schedule 3 hours for each subject
    hours_scheduled = 0
    max_attempts = 10  # Maximum attempts to find a slot
    attempts = 0

    while hours_scheduled < 3 and attempts < max_attempts:
        teacher = random.choice(available_teacher_subjects)
        room = random.choice(rooms)

        # Randomly select a time slot
        time_slot = random.choice(time_slots)
        slot_id, day, start_time, end_time = time_slot

        # Check if the slot is already assigned
        if slot_id not in assigned_slots:
            assigned_slots.add(slot_id)
            hours_scheduled += 1  # Increment scheduled hours

            # Insert into schedule
            print(f"Inserting: {subject_code} - {teacher[1]} in {room[1]} at {day} {start_time}-{end_time}")
            cursor.execute(
                "INSERT INTO schedule (subject_code, teacher_name, room_name, day, start_time, end_time) VALUES (%s, %s, %s, %s, %s, %s)",
                (subject_code, teacher[1], room[1], day, start_time, end_time)
            )
        else:
            print(f"⚠ Slot {slot_id} already assigned, trying another slot...")

        attempts += 1

    if hours_scheduled < 3:
        print(f"❌ Failed to schedule all hours for {subject_code} after {attempts} attempts.")
        unassigned_subjects.append((subject_code, "Failed to schedule all hours after maximum attempts"))

# Commit the schedule to the database
conn.commit()

# Create a view to see the classes of each program during the week, including year level
print("Creating view for weekly schedule by program...")
create_view_query = """
CREATE OR REPLACE VIEW weekly_schedule AS
SELECT 
    s.subject_code,
    sub.program,
    sub.year_level,
    s.teacher_name,
    s.room_name,
    s.day,
    s.start_time,
    s.end_time
FROM 
    schedule s
JOIN 
    subjects sub ON s.subject_code = sub.subject_code
ORDER BY 
    sub.program, s.day, s.start_time;
"""

cursor.execute(create_view_query)
print("View 'weekly_schedule' created successfully.")

# Function to fetch and display the weekly schedule
def fetch_weekly_schedule(cursor):
    print("\n=== Weekly Schedule ===")
    cursor.execute("SELECT * FROM weekly_schedule")
    schedule_rows = cursor.fetchall()
    
    for row in schedule_rows:
        subject_code, program, year_level, teacher_name, room_name, day, start_time, end_time = row
        print(f"Program: {program}, Year Level: {year_level}, Subject: {subject_code}, Teacher: {teacher_name}, Room: {room_name}, Day: {day}, Time: {start_time} - {end_time}")

# Fetch and display the weekly schedule
fetch_weekly_schedule(cursor)

# Export the weekly schedule to a CSV file
def export_to_csv(cursor, filename):
    cursor.execute("SELECT * FROM weekly_schedule")
    rows = cursor.fetchall()
    
    with open(filename, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        # Write the header
        writer.writerow(['Subject Code', 'Program', 'Year Level', 'Teacher Name', 'Room Name', 'Day', 'Start Time', 'End Time'])
        # Write the data
        for row in rows:
            writer.writerow(row)
    
    print(f"Data exported to {filename} successfully.")

# Call the export function
export_to_csv(cursor, 'weekly_schedule.csv')

# Summary of assigned and unassigned subjects
print("\n=== Summary of Assigned and Unassigned Subjects ===")
print("Assigned Subjects:")
if len(subjects) - len(unassigned_subjects) > 0:
    for subject in subjects:
        subject_code, subject_name, program, year_level, lecture_hours = subject
        if subject_code not in [unassigned[0] for unassigned in unassigned_subjects]:
            print(f"Subject Code: {subject_code} - Program: {program}, Year Level: {year_level}")
else:
    print("All subjects were unassigned.")

print("\nUnassigned Subjects:")
if unassigned_subjects:
    for subject_code, reason in unassigned_subjects:
        print(f"Subject Code: {subject_code} - Reason: {reason}")
else:
    print("All subjects were successfully scheduled.")

# Close the connection
conn.close()

print("✅ Schedule generation process completed!")