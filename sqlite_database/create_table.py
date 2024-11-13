import sqlite3

# Connects to an existing database or creates a new one
conn = sqlite3.connect('grp6_senior_thesis.db')
cursor = conn.cursor()

# Create table
cursor.execute('''
CREATE TABLE IF NOT EXISTS images (
    frame_path TEXT NOT NULL,
    video_ID TEXT NOT NULL,
    time_frame TEXT PRIMARY KEY NOT NULL 
)
''')

# Upload keyframes
cursor.execute("INSERT INTO users (name, age) VALUES (?, ?)", ("Alice", 25))
conn.commit()
