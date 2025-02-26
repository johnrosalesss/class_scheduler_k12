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
print(f"Fetched {len(subjects)} subjects.")

print("Loading teachers with their subjects...")
cursor.execute("""
    SELECT t.teacher_id, CONCAT(t.teacher_first_name, ' ', t.teacher_last_name) AS teacher_name, t.subject_name
    FROM teachers t
""")
teacher_subjects = cursor.fetchall()
print(f"Fetched {len(teacher_subjects)} teachers with subjects.")

print("Loading rooms...")
cursor.execute("SELECT * FROM rooms")
rooms = cursor.fetchall()
print(f"Fetched {len(rooms)} rooms.")

print("Loading time slots...")
cursor.execute("SELECT * FROM time_slots")
time_slots = cursor.fetchall()
print(f"Fetched {len(time_slots)} time slots.")

# Load sections
print("Loading sections...")
cursor.execute("SELECT * FROM sections")
sections = cursor.fetchall()
print(f"Fetched {len(sections)} sections.")

# Clear old schedule
print("Clearing old schedule...")
cursor.execute("DELETE FROM schedule")

# Prepare to track assigned slots and unassigned subjects
unassigned_subjects = []

# Schedule each subject for the required lecture hours
for subject in subjects:
    subject_code, subject_name, program, year_level, hours_per_week, semester = subject  

    # Find available teachers for the current subject
    available_teacher_subjects = []
    for teacher in teacher_subjects:
        teacher_id, teacher_name, teacher_subjects_list = teacher
        # Split the teacher's subjects into a list
        teacher_subjects_list = teacher_subjects_list.split(', ')
        
        # Check if the current subject is in the teacher's list of subjects
        if subject_name in teacher_subjects_list:
            available_teacher_subjects.append((teacher_id, teacher_name))

    if not available_teacher_subjects:
        print(f"⚠ No teacher available for {subject_name}, skipping...")
        unassigned_subjects.append((subject_code, "No available teacher"))
        continue


    # Schedule required hours for each subject
    hours_scheduled = 0
    max_attempts = 10  # Maximum attempts to find a slot
    attempts = 0

    while hours_scheduled < hours_per_week and attempts < max_attempts:
        teacher_id, teacher_name = random.choice(available_teacher_subjects)
        room = random.choice(rooms)
        time_slot = random.choice(time_slots)

        # Extract time slot details
        slot_id, day, start_time, end_time = time_slot

        # Check for recess and lunch breaks based on year level
        if (program == "Grade School" and (
            (start_time >= "10:00" and end_time <= "10:30") or  # Recess after 2nd period
            (start_time >= "12:00" and end_time <= "13:00")  # Lunch after 4th period
        )) or (program == "High School" and (
            (start_time >= "11:00" and end_time <= "11:30") or  # Recess after 3rd period
            (start_time >= "12:00" and end_time <= "13:00")  # Lunch after 4th period
        )):
            print(f"⚠ Slot {slot_id} is during recess/lunch for {program}, trying another slot...")
            attempts += 1
            continue

        # Check for hard constraints
        cursor.execute("""
            SELECT COUNT(*) FROM schedule 
            WHERE (teacher_name = %s AND day = %s AND start_time < %s AND end_time > %s) OR
                  (room_name = %s AND day = %s AND start_time < %s AND end_time > %s)
        """, (teacher_name, day, end_time, start_time, room[1], day, end_time, start_time))
        conflicts = cursor.fetchone()[0]

        if conflicts > 0:
            print(f"⚠ Conflict detected for {subject_code} with {teacher_name} in {room[1]} at {day} {start_time}-{end_time}, trying another slot...")
            attempts += 1
            continue

        # Check if the slot is available for the subject, room, and teacher
        cursor.execute("""
            SELECT COUNT(*) FROM schedule 
            WHERE subject_code = %s AND day = %s AND start_time = %s AND end_time = %s AND room_name = %s
        """, (subject_code, day, start_time, end_time, room[1]))
        count = cursor.fetchone()[0]

        if count < 1:  # If no existing schedule for this subject at this time and room
            hours_scheduled += 1  # Increment scheduled hours
            # Insert into schedule
            print(f"Inserting: {subject_code} - {teacher_name} in {room[1]} at {day} {start_time}-{end_time}")
            cursor.execute(
                "INSERT INTO schedule (subject_code, teacher_name, room_name, day, start_time, end_time) VALUES (%s, %s, %s, %s, %s, %s)",
                (subject_code, teacher_name, room[1], day, start_time, end_time)
            )
        else:
            print(f"⚠ Slot {slot_id} already assigned for {subject_code} in room {room[1]}, trying another slot...")

        attempts += 1

    if hours_scheduled < hours_per_week:
        print(f"❌ Failed to schedule all hours for {subject_code} after {attempts} attempts.")
        unassigned_subjects.append((subject_code, "Failed to schedule all hours after maximum attempts"))

# Schedule homeroom periods
for section in sections:
    section_id, program, year_level, num_students, section_name, adviser_last_name, adviser_first_name = section

    # Determine the day for homeroom based on the program
    if program == "Grade School":
        # Homeroom can be scheduled any day for 1 hour
        for day in ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]:
            time_slot = ("09:00", "10:00")  # Example time for homeroom
            cursor.execute("""
                SELECT COUNT(*) FROM schedule 
                WHERE day = %s AND start_time = %s AND end_time = %s
            """, (day, time_slot[0], time_slot[1]))
            count = cursor.fetchone()[0]

            if count < 1:  # If no existing schedule for this time
                print(f"Inserting Homeroom for {section_name} on {day} from {time_slot[0]} to {time_slot[1]}")
                cursor.execute(
                    "INSERT INTO schedule (subject_code, teacher_name, room_name, day, start_time, end_time) VALUES (%s, %s, %s, %s, %s, %s)",
                    ("Homeroom", f"{adviser_first_name} {adviser_last_name}", "Homeroom Room", day, time_slot[0], time_slot[1])
                )
                break  # Exit after scheduling homeroom for this section

    elif program == "High School":
        # Homeroom is scheduled on Friday during the 1st period
        day = "Friday"
        time_slot = ("08:00", "09:00")  # Example time for homeroom
        cursor.execute("""
            SELECT COUNT(*) FROM schedule 
            WHERE day = %s AND start_time = %s AND end_time = %s
        """, (day, time_slot[0], time_slot[1]))
        count = cursor.fetchone()[0]

        if count < 1:  # If no existing schedule for this time
            print(f"Inserting Homeroom for {section_name} on {day} from {time_slot[0]} to {time_slot[1]}")
            cursor.execute(
                "INSERT INTO schedule (subject_code, teacher_name, room_name, day, start_time, end_time) VALUES (%s, %s, %s, %s, %s, %s)",
                ("Homeroom", f"{adviser_first_name} {adviser_last_name}", "Homeroom Room", day, time_slot[0], time_slot[1])
            )

# Commit the schedule to the database
conn.commit()
# Existing code...

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

# Create a view for room schedules
print("Creating view for room schedules...")
create_room_schedules_view = """
CREATE OR REPLACE VIEW room_schedules AS
SELECT 
    s.room_name,
    s.subject_code,
    sub.subject_name,
    s.teacher_name,
    s.day,
    s.start_time,
    s.end_time
FROM 
    schedule s
JOIN 
    subjects sub ON s.subject_code = sub.subject_code
ORDER BY 
    s.room_name, s.day, s.start_time;
"""

cursor.execute(create_room_schedules_view)
print("View 'room_schedules' created successfully.")

# Create a view for teacher subjects
print("Creating view for teacher subjects...")
create_teacher_subjects_view = """
CREATE OR REPLACE VIEW teacher_subjects AS
SELECT 
    s.teacher_name,
    s.subject_code,
    sub.subject_name,
    s.room_name,
    s.day,
    s.start_time,
    s.end_time
FROM 
    schedule s
JOIN 
    subjects sub ON s.subject_code = sub.subject_code
ORDER BY 
    s.teacher_name, s.day, s.start_time;
"""

cursor.execute(create_teacher_subjects_view)
print("View 'teacher_subjects' created successfully.")

# Function to fetch and display the weekly schedule
def fetch_weekly_schedule(cursor):
    print("\n=== Weekly Schedule ===")
    cursor.execute("SELECT * FROM weekly_schedule")
    schedule_rows = cursor.fetchall()
    
    for row in schedule_rows:
        subject_code, subject_name, program, year_level, teacher_name, room_name, day, start_time, end_time = row
        print(f"Program: {program}, Year Level: {year_level}, Subject: {subject_code} - {subject_name}, Teacher: {teacher_name}, Room: {room_name}, Day: {day}, Time: {start_time} - {end_time}")

# Fetch and display the room schedules
def fetch_room_schedules(cursor):
    print("\n=== Room Schedules ===")
    cursor.execute("SELECT * FROM room_schedules")
    room_schedule_rows = cursor.fetchall()
    
    for row in room_schedule_rows:
        room_name, subject_code, subject_name, teacher_name, day, start_time, end_time = row
        print(f"Room: {room_name}, Subject: {subject_code} - {subject_name}, Teacher: {teacher_name}, Day: {day}, Time: {start_time} - {end_time}")

# Fetch and display the teacher subjects
def fetch_teacher_subjects(cursor):
    print("\n=== Teacher Subjects ===")
    cursor.execute("SELECT * FROM teacher_subjects")
    teacher_subject_rows = cursor.fetchall()
    
    for row in teacher_subject_rows:
        teacher_name, subject_code, subject_name, room_name, day, start_time, end_time = row
        print(f"Teacher: {teacher_name}, Subject: {subject_code} - {subject_name}, Room: {room_name}, Day: {day}, Time: {start_time} - {end_time}")

# Fetch and display the weekly schedule
fetch_weekly_schedule(cursor)

# Fetch and display the room schedules
fetch_room_schedules(cursor)

# Fetch and display the teacher subjects
fetch_teacher_subjects(cursor)

# Existing code continues...

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
    _, _, _, year_level, _, _ = subject
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
        subject_code, subject_name, program, year_level, hours_per_week, semester = subject
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