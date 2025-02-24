import mysql.connector
import pandas as pd

conn = mysql.connector.connect(host="localhost", user="root", password="", database="class_scheduler")
cursor = conn.cursor()
cursor.execute("SELECT * FROM schedule")
schedule = cursor.fetchall()
conn.close()

df = pd.DataFrame(schedule, columns=["ID", "Subject", "Teacher", "Room", "Day", "Start Time", "End Time"])
df.to_excel("schedule.xlsx", index=False)
print("Schedule exported to schedule.xlsx")
