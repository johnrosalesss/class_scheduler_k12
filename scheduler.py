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

unassigned_subjects = []  # To track subjects that couldn't be assigned at all
partially_assigned_subjects = []  # To track subjects with some hours unassigned
assigned_subjects = []    # To track successfully assigned subjects

# Dictionary to store the count of successfully scheduled subjects per section
section_schedule_counts = {}

# Debug: Print all subjects in the database
print("All subjects in the database:")
for subject in subjects:
    print(f"Subject: {subject[1]}, Program: {subject[2]}, Year Level: {subject[3]}")

# Schedule each subject for the required lecture hours
for section in sections:
    section_id, program, year_level, num_students, section_name, adviser_last_name, adviser_first_name = section
    print(f"\nProcessing section: {section_name} (Program: {program}, Year Level: {year_level})")
    
    # Convert program and year_level to match the subjects table
    program_str = program.replace('Grade ', '').strip().lower() if program.startswith('Grade ') else program.strip().lower()
    year_level_str = "toddler" if year_level == 0 else f"grade {year_level}".strip().lower()
    
    # Debug: Print the values being compared
    print(f"Looking for subjects with program: {program_str}, year_level: {year_level_str}")
    
    # Get subjects for the current section based on program and year level
    section_subjects = [
        subject for subject in subjects 
        if str(subject[3]).strip().lower() == year_level_str
        and str(subject[2]).strip().lower() == program_str
    ]
    print(f"Found subjects: {section_subjects}")

    # Initialize the count of successfully scheduled subjects for this section
    section_schedule_counts[section_name] = {"year_level": year_level, "count": 0}

    # Schedule subjects for this section
    for subject in section_subjects:
        subject_code, subject_name, program, year_level, hours_per_week, semester = subject
        print(f"\nScheduling subject: {subject_name} (Code: {subject_code}, Hours/Week: {hours_per_week})")
        
        # Find available teachers for the current subject
        available_teacher_subjects = []
        for teacher in teacher_subjects:
            teacher_id, teacher_name, teacher_subjects_list = teacher
            teacher_subjects_list = teacher_subjects_list.split(', ')
            
            if subject_name in teacher_subjects_list:
                available_teacher_subjects.append((teacher_id, teacher_name))
        print(f"Available teachers for {subject_name}: {available_teacher_subjects}")

        if not available_teacher_subjects:
            print(f"⚠ No teacher available for {subject_name} in {section_name}, skipping...")
            unassigned_subjects.append((subject_code, section_name, "No available teacher"))
            continue

        # Initialize hours_scheduled before starting to schedule
        hours_scheduled = 0
        max_attempts = 50  # Increased to allow more attempts
        attempts = 0

        while hours_scheduled < hours_per_week and attempts < max_attempts:
            teacher_id, teacher_name = random.choice(available_teacher_subjects)
            room = random.choice(rooms)
            time_slot = random.choice(time_slots)

            slot_id, day, start_time, end_time = time_slot
            print(f"Attempt {attempts + 1}: Trying slot {slot_id} ({day} {start_time}-{end_time}) with teacher {teacher_name} in room {room[1]}")

            # Check for recess and lunch breaks
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

            # Check for conflicts
            cursor.execute("""
                SELECT COUNT(*) FROM schedule 
                WHERE (teacher_name = %s AND day = %s AND start_time < %s AND end_time > %s) OR
                      (room_name = %s AND day = %s AND start_time < %s AND end_time > %s)
            """, (teacher_name, day, end_time, start_time, room[1], day, end_time, start_time))
            conflicts = cursor.fetchone()[0]
            print(f"Conflicts detected: {conflicts}")

            if conflicts > 0:
                print(f"⚠ Conflict detected for {subject_code} with {teacher_name} in {room[1]} at {day} {start_time}-{end_time}, trying another slot...")
                attempts += 1
                continue

            # Ensure no existing schedule for the subject in the specific section
            cursor.execute("""
                SELECT COUNT(*) FROM schedule 
                WHERE subject_code = %s AND section_id = %s AND day = %s AND start_time = %s AND end_time = %s AND room_name = %s
            """, (subject_code, section_id, day, start_time, end_time, room[1]))
            count = cursor.fetchone()[0]
            print(f"Existing schedules for this subject: {count}")

            if count < 1:  # If no existing schedule for this subject at this time and room
                hours_scheduled += 1
                print(f"✅ Inserting: {subject_code} for section {section_name} - {teacher_name} in {room[1]} at {day} {start_time}-{end_time}")
                cursor.execute(
                    "INSERT INTO schedule (subject_code, teacher_name, room_name, day, start_time, end_time, section_id) VALUES (%s, %s, %s, %s, %s, %s, %s)",
                    (subject_code, teacher_name, room[1], day, start_time, end_time, section_id)
                )
                assigned_subjects.append((subject_code, section_name, teacher_name, room[1], day, start_time, end_time))
                section_schedule_counts[section_name]["count"] += 1  # Increment the count for this section
            else:
                print(f"⚠ Slot {slot_id} already assigned for {subject_code} in {section_name}, trying another slot...")

            attempts += 1

        if hours_scheduled < hours_per_week:
            if hours_scheduled == 0:
                print(f"❌ Failed to schedule any hours for {subject_code} in {section_name} after {attempts} attempts.")
                unassigned_subjects.append((subject_code, section_name, "Failed to schedule any hours after maximum attempts"))
            else:
                print(f"⚠ Partially scheduled {hours_scheduled}/{hours_per_week} hours for {subject_code} in {section_name}.")
                partially_assigned_subjects.append((subject_code, section_name, f"Partially scheduled {hours_scheduled}/{hours_per_week} hours"))

# After running the schedule process, print unassigned subjects with reasons
if unassigned_subjects:
    print("\nUnassigned Subjects with Reasons:")
    for subject_code, section_name, reason in unassigned_subjects:  # Unpack all three values
        print(f"Subject: {subject_code}, Section: {section_name}, Reason: {reason}")
else:
    print("All subjects assigned successfully.")

# Print the summary of assigned subjects
print("\nAssigned Subjects:")
if assigned_subjects:
    for subject_code, section_name, teacher_name, room_name, day, start_time, end_time in assigned_subjects:
        print(f"Subject: {subject_code}, Section: {section_name}, Teacher: {teacher_name}, Room: {room_name}, Day: {day}, Time: {start_time}-{end_time}")
else:
    print("No subjects assigned.")

# Print the number of successfully scheduled subjects per section
print("\nSuccessfully Scheduled Subjects per Section:")
for section_name, data in section_schedule_counts.items():
    print(f"Section: {section_name}, Year Level: {data['year_level']}, Successfully Scheduled Subjects: {data['count']}")

# Schedule homeroom periods
for section in sections:
    section_id, program, year_level, num_students, section_name, adviser_last_name, adviser_first_name = section

    # Determine the day for homeroom based on the program
    homeroom_scheduled = False
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
                    "INSERT INTO schedule (subject_code, teacher_name, room_name, day, start_time, end_time, section_id) VALUES (%s, %s, %s, %s, %s, %s, %s)",
                    ("Homeroom", f"{adviser_first_name} {adviser_last_name}", "Homeroom Room", day, time_slot[0], time_slot[1], section_id)
                )
                homeroom_scheduled = True
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
                "INSERT INTO schedule (subject_code, teacher_name, room_name, day, start_time, end_time, section_id) VALUES (%s, %s, %s, %s, %s, %s, %s)",
                ("Homeroom", f"{adviser_first_name} {adviser_last_name}", "Homeroom Room", day, time_slot[0], time_slot[1], section_id)
            )

# Commit the schedule to the database
conn.commit()

# Create a view to summarize schedules assigned to each section
create_view_query = """
CREATE OR REPLACE VIEW section_schedule_summary AS
SELECT 
    s.section_id,
    sec.section_name,
    sec.program,
    sec.year_level,
    s.subject_code,
    sub.subject_name,
    s.teacher_name,
    s.room_name,
    s.day,
    s.start_time,
    s.end_time
FROM 
    schedule s
JOIN 
    sections sec ON s.section_id = sec.section_id
JOIN 
    subjects sub ON s.subject_code = sub.subject_code
ORDER BY 
    sec.section_name, s.day, s.start_time;
"""
cursor.execute(create_view_query)
print("View 'section_schedule_summary' created successfully.")

# Export the view to a CSV file
def export_view_to_csv(cursor, view_name, filename):
    cursor.execute(f"SELECT * FROM {view_name}")
    rows = cursor.fetchall()
    
    with open(filename, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        # Write the header
        writer.writerow(['Section ID', 'Section Name', 'Program', 'Year Level', 'Subject Code', 'Subject Name', 'Teacher Name', 'Room Name', 'Day', 'Start Time', 'End Time'])
        # Write the data
        for row in rows:
            writer.writerow(row)
    
    print(f"View '{view_name}' exported to {filename} successfully.")

# Call the export function for the view
export_view_to_csv(cursor, 'section_schedule_summary', 'section_schedule_summary.csv')

# Export room schedules to CSV
def export_room_schedules_to_csv(cursor, filename):
    cursor.execute("""
        SELECT room_name, day, start_time, end_time, subject_code, section_id, teacher_name
        FROM schedule
        ORDER BY room_name, day, start_time
    """)
    rows = cursor.fetchall()
    
    with open(filename, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        # Write the header
        writer.writerow(['Room Name', 'Day', 'Start Time', 'End Time', 'Subject Code', 'Section ID', 'Teacher Name'])
        # Write the data
        for row in rows:
            writer.writerow(row)
    
    print(f"Room schedules exported to {filename} successfully.")

export_room_schedules_to_csv(cursor, 'room_schedules.csv')

# Export teacher subjects to CSV
def export_teacher_subjects_to_csv(cursor, filename):
    cursor.execute("""
        SELECT teacher_id, CONCAT(teacher_first_name, ' ', teacher_last_name) AS teacher_name, subject_name
        FROM teachers
    """)
    rows = cursor.fetchall()
    
    with open(filename, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        # Write the header
        writer.writerow(['Teacher ID', 'Teacher Name', 'Subject Name'])
        # Write the data
        for row in rows:
            writer.writerow(row)
    
    print(f"Teacher subjects exported to {filename} successfully.")

export_teacher_subjects_to_csv(cursor, 'teacher_subjects.csv')

# Close connection
cursor.close()
conn.close()
print("✅ Schedule generation process completed!")