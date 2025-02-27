import mysql.connector
import csv
import os

def export_section_schedule_summary(cursor, filename):
    cursor.execute("SELECT * FROM section_schedule_summary")
    rows = cursor.fetchall()
    
    with open(filename, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        # Write the header
        writer.writerow(['Section ID', 'Semester', 'Section Name', 'Program', 'Year Level', 'Subject Code', 
                         'Subject Name', 'Teacher Name', 'Room Name', 'Day', 'Start Time', 'End Time'])
        # Write the data
        for row in rows:
            writer.writerow(row)
    
    print(f"View 'section_schedule_summary' exported to {filename} successfully.")

def export_filtered_section_schedules_to_csv(cursor):
    cursor.execute("SELECT DISTINCT section_name, program, year_level FROM section_schedule_summary")
    sections = cursor.fetchall()
    
    # Create directory for section schedules if it doesn't exist
    output_dir = 'section_schedule_csv'
    os.makedirs(output_dir, exist_ok=True)

    for section in sections:
        section_name, program, year_level = section  # Unpack the tuple
        cursor.execute("""
            SELECT * FROM section_schedule_summary 
            WHERE section_name = %s AND program = %s AND year_level = %s
        """, (section_name, program, year_level))
        rows = cursor.fetchall()
        
        if rows:
            # Create a valid filename
            filename = f"{section_name.replace(' ', '_')}_{program.replace(' ', '_')}_{year_level}.csv"
            filepath = os.path.join(output_dir, filename)
            with open(filepath, mode='w', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                # Write the header
                writer.writerow(['Section ID', 'Semester', 'Section Name', 'Program', 'Year Level', 'Subject Code', 
                                 'Subject Name', 'Teacher Name', 'Room Name', 'Day', 'Start Time', 'End Time'])
                # Write the data
                for row in rows:
                    writer.writerow(row)
            
            print(f"Section schedule for '{section_name}', '{program}', '{year_level}' exported to {filepath} successfully.")

def export_view_to_csv(cursor, view_name, filename):
    cursor.execute(f"SELECT * FROM {view_name}")
    rows = cursor.fetchall()
    
    with open(filename, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        # Write the header
        writer.writerow(['Section ID', 'Semester', 'Subject Code', 'Subject Name', 'Program', 'Year Level', 'Teacher Name', 'Room Name', 'Day', 'Start Time', 'End Time'])
        # Write the data
        for row in rows:
            writer.writerow(row)
    
    print(f"View '{view_name}' exported to {filename} successfully.")

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

def export_teacher_schedules_to_csv(cursor):
    cursor.execute("SELECT DISTINCT teacher_id, CONCAT(teacher_first_name, ' ', teacher_last_name) AS teacher_name FROM teachers")
    teachers = cursor.fetchall()
    
    # Create directory for teacher schedules if it doesn't exist
    output_dir = 'teacher_schedule_csv'
    os.makedirs(output_dir, exist_ok=True)

    for teacher in teachers:
        teacher_id, teacher_name = teacher  # Unpack the tuple
        cursor.execute("""
            SELECT * FROM section_schedule_summary 
            WHERE teacher_name = %s
        """, (teacher_name,))
        rows = cursor.fetchall()
        
        if rows:
            # Create a valid filename
            filename = f"{teacher_name.replace(' ', '_')}_schedule.csv"
            filepath = os.path.join(output_dir, filename)
            with open(filepath, mode='w', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                # Write the header
                writer.writerow(['Section ID', 'Semester', 'Section Name', 'Program', 'Year Level', 'Subject Code', 
                                 'Subject Name', 'Teacher Name', 'Room Name', 'Day', 'Start Time', 'End Time'])
                # Write the data
                for row in rows:
                    writer.writerow(row)
            
            print(f"Teacher schedule for '{teacher_name}' exported to {filepath} successfully.")

def export_sections_to_csv(cursor, filename):
    cursor.execute("SELECT * FROM sections")
    sections = cursor.fetchall()
    
    # Get column names
    column_names = [i[0] for i in cursor.description]
    
    with open(filename, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(column_names)  # Write header
        writer.writerows(sections)  # Write data rows
    
    print(f"✅ Data from 'sections' table exported successfully to {filename}")

def export_subjects_to_csv(cursor, filename):
    cursor.execute("SELECT * FROM subjects")
    subjects = cursor.fetchall()
    
    with open(filename, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        # Write the header
        writer.writerow(['Subject Code', 'Subject Name', 'Program', 'Year Level', 'Hours Per Week', 'Semester'])
        # Write the data
        for subject in subjects:
            writer.writerow(subject)
    
    print(f"Subjects exported to {filename} successfully!")

def export_teachers_to_csv(cursor, filename):
    cursor.execute("SELECT * FROM teachers")
    teachers = cursor.fetchall()
    
    with open(filename, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        # Write header
        writer.writerow([i[0] for i in cursor.description])
        # Write data
        writer.writerows(teachers)
    
    print(f"Teachers data exported to {filename} successfully.")

def create_view(cursor):
    create_view_query = """
    CREATE OR REPLACE VIEW section_schedule_summary AS
    SELECT 
        s.section_id,
        s.semester,
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

def main():
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

    # Create the view
    create_view(cursor)

    # Export the view to CSV
    export_view_to_csv(cursor, 'weekly_schedule', 'weekly_schedule.csv')

    # Export room schedules to CSV
    export_room_schedules_to_csv(cursor, 'room_schedules.csv')

    # Export teacher subjects to CSV
    export_teacher_subjects_to_csv(cursor, 'teacher_subjects.csv')

    # Export teacher schedules to CSV
    export_teacher_schedules_to_csv(cursor)

    # Export sections to CSV
    export_sections_to_csv(cursor, 'sections.csv')

    # Export subjects to CSV
    export_subjects_to_csv(cursor, 'subjects.csv')

    # Export teachers to CSV
    export_teachers_to_csv(cursor, 'teachers.csv')
    
    # Export section schedule summary to CSV
    export_section_schedule_summary(cursor, 'section_schedule_summary.csv')

    # Export filtered section schedules to CSV
    export_filtered_section_schedules_to_csv(cursor)

    # Close connection
    cursor.close()
    conn.close()

if __name__ == "__main__":
    main()