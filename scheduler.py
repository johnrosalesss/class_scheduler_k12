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

print("Loading teacher_subjects with teacher names...")
cursor.execute("""
    SELECT ts.teacher_id, t.teacher_name, ts.subject_code
    FROM teacher_subjects ts
    JOIN teachers t ON ts.teacher_id = t.teacher_id
""")
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
unassigned_subjects = []

# Schedule each subject for the required lecture hours
for subject in subjects:
    subject_code, subject_name, program, year_level, lecture_hours = subject  

    available_teacher_subjects = [(t[0], t[1]) for t in teacher_subjects if t[2] == subject_code]
    if not available_teacher_subjects:
        print(f"⚠ No teacher available for {subject_code}, skipping...")
        unassigned_subjects.append((subject_code, "No available teacher"))
        continue

    # Schedule required hours for each subject
    hours_scheduled = 0
    max_attempts = 10  # Maximum attempts to find a slot
    attempts = 0

    while hours_scheduled < lecture_hours and attempts < max_attempts:
        teacher_id, teacher_name = random.choice(available_teacher_subjects)
        room = random.choice(rooms)

        # Randomly select a time slot
        time_slot = random.choice(time_slots)
        slot_id, day, start_time, end_time = time_slot

        # Check if the slot is available
        cursor.execute("""
            SELECT COUNT(*) FROM schedule 
            WHERE subject_code = %s AND day = %s AND start_time = %s AND end_time = %s
        """, (subject_code, day, start_time, end_time))
        count = cursor.fetchone()[0]

        if count < 1:  # If no existing schedule for this subject at this time
            hours_scheduled += 1  # Increment scheduled hours

            # Insert into schedule
            print(f"Inserting: {subject_code} - {teacher_name} in {room[1]} at {day} {start_time}-{end_time}")
            cursor.execute(
                "INSERT INTO schedule (subject_code, teacher_name, room_name, day, start_time, end_time) VALUES (%s, %s, %s, %s, %s, %s)",
                (subject_code, teacher_name, room[1], day, start_time, end_time)
            )
        else:
            print(f"⚠ Slot {slot_id} already assigned for {subject_code}, trying another slot...")

        attempts += 1

    if hours_scheduled < lecture_hours:
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
    sub.subject_name,
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
        subject_code, subject_name, program, year_level, teacher_name, room_name, day, start_time, end_time = row
        print(f"Program: {program}, Year Level: {year_level}, Subject: {subject_code} - {subject_name}, Teacher: {teacher_name}, Room: {room_name}, Day: {day}, Time: {start_time} - {end_time}")

# Fetch and display the weekly schedule
fetch_weekly_schedule(cursor)

# Export the weekly schedule to a CSV file
def export_to_csv(cursor, filename):
    cursor.execute("SELECT * FROM weekly_schedule")
    rows = cursor.fetchall()
    
    with open(filename, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        # Write the header
        writer.writerow(['Subject Code', 'Subject Name', 'Program', 'Year Level', 'Teacher Name', 'Room Name', 'Day', 'Start Time', 'End Time'])
        # Write the data
        for row in rows:
            writer.writerow(row)
    
    print(f"Data exported to {filename} successfully.")

# Call the export function for the weekly schedule
export_to_csv(cursor, 'weekly_schedule.csv')

# Tally subjects by grade level
grade_levels = [
    "Toddler", "Nursery", "Kinder",
    "Grade 1", "Grade 2", "Grade 3", "Grade 4", "Grade 5", "Grade 6",
    "Grade 7", "Grade 8", "Grade 9", "Grade 10", "Grade 11", "Grade 12"
]

# Initialize a dictionary to hold the tally
subject_tally = {grade: 0 for grade in grade_levels}

# Count subjects for each grade level
for subject in subjects:
    _, _, _, year_level, _ = subject
    if year_level in subject_tally:
        subject_tally[year_level] += 1

# Write the tally to a new CSV file
with open('subject_tally_by_grade.csv', mode='w', newline='', encoding='utf-8') as file:
    writer = csv.writer(file)
    # Write the header
    writer.writerow(['Grade Level', 'Number of Subjects'])
    # Write the tally data
    for grade, count in subject_tally.items():
        writer.writerow([grade, count])

print("Subject tally by grade exported to 'subject_tally_by_grade.csv' successfully.")

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
