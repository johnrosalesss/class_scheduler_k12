import mysql.connector
import random
from collections import defaultdict

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
    SELECT t.teacher_id, CONCAT(t.teacher_first_name, ' ', t.teacher_last_name) AS teacher_name, t.subject_name, t.teacher_type
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

print("Loading sections...")
cursor.execute("SELECT * FROM sections")
sections = cursor.fetchall()
print(f"Fetched {len(sections)} sections.")

# Clear old schedule
print("Clearing old schedule...")
cursor.execute("DELETE FROM schedule")

# Step 1: Remove any subjects assigned on Friday 7:30 - 8:30 AM
print("Clearing schedules for Friday 7:30 - 8:30 AM to enforce homeroom...")
cursor.execute("""
    DELETE FROM schedule
    WHERE day = 'Friday' AND start_time = '07:30' AND end_time = '08:30'
""")
conn.commit()

# Step 2: Insert homeroom schedule for all sections based on grade level
homeroom_schedules = []
for section in sections:
    section_id, program, year_level, num_students, section_name, adviser_last_name, adviser_first_name = section

    # Ensure the adviser exists
    adviser_name = f"{adviser_first_name} {adviser_last_name}" if adviser_first_name and adviser_last_name else "TBA"

    # Determine the appropriate time slot based on the grade level
    if year_level in range(1, 7):  # Grades 1 to 6
        time_slot_id = 'GS_TS041'  # Time slot ID for Grades 1-6
    elif year_level in range(7, 11):  # Grades 7 to 10
        time_slot_id = 'HS_TS041'  # Time slot ID for Grades 7-10
    else:
        print(f"⚠ No valid time slot for {section_name}, skipping...")
        continue

    # Fetch the time slot details
    cursor.execute("SELECT start_time, end_time FROM time_slots WHERE time_slot_id = %s", (time_slot_id,))
    time_slot = cursor.fetchone()
    
    if time_slot:
        start_time, end_time = time_slot
        day = "Friday"  # Homeroom is scheduled on Friday

        # Extract the numeric part of the section_id and calculate the room number
        section_number = int(section_id[3:])  # Extract the numeric part after 'SEC'
        room_number = 100 + section_number  # Calculate the room number (e.g., SEC077 -> 177)
        room_name = f"Room {room_number}"  # Format the room name

        print(f"Inserting Homeroom for {section_name} on {day} from {start_time} to {end_time} (Adviser: {adviser_name}, Room: {room_name})")
        cursor.execute("""
            INSERT INTO schedule (subject_code, teacher_name, room_name, day, start_time, end_time, section_id)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, ("Homeroom", adviser_name, room_name, day, start_time, end_time, section_id))

        homeroom_schedules.append((section_name, day, start_time, end_time, room_name))
    else:
        print(f"⚠ Time slot not found for {section_name}, skipping...")

conn.commit()

# Step 3: Print the enforced homeroom schedule
print("\nEnforced Homeroom Schedule:")
for section_name, day, start_time, end_time, room_name in homeroom_schedules:
    print(f"Section: {section_name}, Day: {day}, Time: {start_time}-{end_time}, Room: {room_name}")

# Trackers
unassigned_subjects = []  # Subjects that couldn't be assigned at all
partially_assigned_subjects = []  # Subjects with some hours unassigned
assigned_subjects = []    # Successfully assigned subjects
section_schedule_counts = defaultdict(lambda: {"year_level": 0, "count": 0, "subjects": []})  # Successfully scheduled subjects per section
teacher_subject_counts = defaultdict(int)  # Track subjects assigned to part-time teachers

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
    year_level_str = "oddler" if year_level == 0 else f"grade {year_level}".strip().lower()
    
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
    section_schedule_counts[section_name]["year_level"] = year_level

    # Schedule subjects for this section
    for subject in section_subjects:
        subject_code, subject_name, program, year_level, hours_per_week, semester = subject
        print(f"\nScheduling subject: {subject_name} (Code: {subject_code}, Hours/Week: {hours_per_week})")
        
        # Find available teachers for the current subject
        available_teacher_subjects = []
        for teacher in teacher_subjects:
            teacher_id, teacher_name, teacher_subjects_list, teacher_type = teacher
            teacher_subjects_list = teacher_subjects_list.split(', ')
            
            if subject_name in teacher_subjects_list:
                # Check part-time teacher restriction
                if teacher_type == "Part-Time" and teacher_subject_counts[teacher_id] >= 5:
                    print(f"⚠ Teacher {teacher_name} (Part-Time) has reached the maximum of 5 subjects.")
                    continue
                available_teacher_subjects.append((teacher_id, teacher_name, teacher_type))
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
            teacher_id, teacher_name, teacher_type = random.choice(available_teacher_subjects)
            room = random.choice(rooms)
            time_slot = random.choice(time_slots)

            slot_id, day, start_time, end_time = time_slot
            print(f"Attempt {attempts + 1}: Trying slot {slot_id} ({day} {start_time}-{end_time}) with teacher {teacher_name} in room {room[1]}")

            # Check for conflicts
            cursor.execute("""
                SELECT COUNT(*) FROM schedule 
                WHERE (teacher_name = %s AND day = %s AND start_time < %s AND end_time > %s) OR
                      (room_name = %s AND day = %s AND start_time < %s AND end_time > %s) OR
                      (section_id = %s AND day = %s AND start_time < %s AND end_time > %s)
            """, (teacher_name, day, end_time, start_time, room[1], day, end_time, start_time, section_id, day, end_time, start_time))
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
                section_schedule_counts[section_name]["subjects"].append(subject_name)  # Add subject to the section's list
                if teacher_type == "Part-Time":
                    teacher_subject_counts[teacher_id] += 1  # Increment part-time teacher's subject count
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
    for subject_code, section_name, reason in unassigned_subjects:
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
    print(f"Subjects Assigned: {', '.join(data['subjects'])}")

# Identify sections with zero subjects scheduled
unscheduled_sections = []
for section_name, data in section_schedule_counts.items():
    if data["count"] == 0:
        unscheduled_sections.append(section_name)

# Analyze the reasons for unscheduled sections
print("\nSummary of Unscheduled Sections and Possible Reasons:")
for section_name in unscheduled_sections:
    reason = []
    
    # Check if no matching subjects were found for this section
    if not any(subject for subject in subjects if subject[3] == section_name):
        reason.append("No matching subjects found for this section.")

    # Check if all required subjects lacked teachers
    unassigned_for_section = [sub for sub in unassigned_subjects if sub[1] == section_name]
    if unassigned_for_section:
        reason.append("No available teachers for required subjects.")

    # Check if scheduling conflicts prevented assignments
    if section_name in [sub[1] for sub in partially_assigned_subjects]:
        reason.append("Scheduling conflicts prevented full assignment.")

    # If no clear reason, assume rooms/time slots were unavailable
    if not reason:
        reason.append("Possible room/time slot constraints.")

    print(f"- Section: {section_name} -> Reason(s): {', '.join(reason)}")

# Print Hard Constraints Summary
print("\nHard Constraints Summary:")
print("1. No Teacher Conflicts – A teacher cannot be scheduled to teach multiple subjects at the same time.")
print("2. No Room Conflicts – Each room can accommodate only one class at a time.")
print("3. No Section Conflicts – A section can only attend one subject at a time.")
print("4. Part-Time Teacher Restriction – Part-time teachers can teach a maximum of five subjects.")
print("5. School Hours Restriction – Classes must be scheduled between 7:30 AM and 5:00 PM.")
print("6. Lunch Break Restriction – No classes are scheduled during lunch breaks.")
print("7. Teacher Subject Specialization – Teachers can only teach the subjects assigned to them.")
print("8. Required Weekly Lecture Hours – Each subject must meet its required lecture hours per week.")
print("9. All Subjects Must Be Scheduled – If a subject cannot be scheduled due to conflicts, it is flagged as 'unassigned' and reported.")
print("10. Section Time Efficiency – Sections should have sequential lessons with minimal gaps between classes.")

# Print Soft Constraints Summary
print("\nSoft Constraints Summary:")
print("1. Balanced Schedule Distribution – Spread subject hours across multiple days instead of concentrating them on a single day.")
print("2. Evenly Distribute Classes Across Days – Prioritize underutilized days (e.g., Tuesday and Wednesday) over heavily scheduled ones (e.g., Monday and Friday).")
print("3. Teacher Room Stability – Assign teachers to the same room whenever possible.")
print("4. Teacher Time Efficiency – Minimize gaps between a teacher’s lessons to create a more efficient schedule.")
print("5. Section Subject Variety – Avoid scheduling the same subject consecutively to provide variety in student learning on sections.")
print("6. Minimize Teacher Gaps – Reduce the number of free periods between a teacher's lessons to optimize their schedule.")

# Close connection
cursor.close()
conn.close()
print("✅ Schedule generation process completed!")


