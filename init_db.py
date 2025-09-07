import sqlite3
from pathlib import Path

DB_PATH = Path('database.db')
SCHEMA_FILE = Path('schema.sql')

def init_db():
    if DB_PATH.exists():
        print("Overwriting existing database 'database.db' (delete file to keep).")
        DB_PATH.unlink()
    conn = sqlite3.connect(DB_PATH)
    conn.executescript(SCHEMA_FILE.read_text())
    conn.commit()
    print("Schema created.")

    cur = conn.cursor()

    #sample colleges
    colleges = ['REVA University', 'PES University', 'RV College']
    for c in colleges:
        cur.execute("INSERT INTO colleges (name) VALUES (?)", (c,))

    #sample students
    students = [
        ("Alice Kumar","alice@example.com",1),
        ("Brunda N","brunda@example.com",1),
        ("Chirag Patel","chirag@example.com",2),
        ("Deepa Rao","deepa@example.com",2),
        ("Esha Singh","esha@example.com",3),
        ("Farhan Ahmed","farhan@example.com",1),
        ("Gita Sharma","gita@example.com",3)
    ]
    cur.executemany("INSERT INTO students (name,email,college_id) VALUES (?,?,?)", students)

    #sample events
    events = [
        ("Hackathon 2025", "24-hr coding hackathon", "Hackathon", 1, "2025-09-10", "2025-09-11"),
        ("AI Workshop", "Intro to AI tools", "Workshop", 1, "2025-08-25", "2025-08-25"),
        ("Tech Talk: Cloud", "Cloud trending topics", "Seminar", 2, "2025-09-05", "2025-09-05"),
        ("Cultural Fest", "Inter-college fest", "Fest", 3, "2025-10-20", "2025-10-21")
    ]
    
    cur.executemany(
        "INSERT INTO events (name,description,type,college_id,start_date,end_date) VALUES (?,?,?,?,?,?)", 
        events
    )

    conn.commit()

    #some registrations
    regs = [
        (1,1), (2,1), (4,1), (6,1), # Hackathon
        (1,2), (3,2),               # AI Workshop
        (3,3), (5,3), (6,3),        # Tech Talk
        (5,4), (7,4)                 # Cultural Fest
    ]
    for s_id, e_id in regs:
        cur.execute("INSERT INTO registrations (student_id,event_id) VALUES (?,?)", (s_id,e_id))

    conn.commit()

    #some attendance
    cur.execute("SELECT id FROM registrations")
    rows = cur.fetchall()
    for i, (rid,) in enumerate(rows[:6], start=1):
        status = 'present' if i % 2 == 1 else 'absent'
        cur.execute("INSERT INTO attendance (registration_id,status) VALUES (?,?)", (rid,status))

    conn.commit()

    #feedback for first 6 registrations
    for i, (rid,) in enumerate(rows[:6], start=1):
        if i % 2 == 1:
            rating = 4
            comment = "Great event"
        else:
            rating = 3
            comment = "Good"
        try:
            cur.execute("INSERT INTO feedback (registration_id,rating,comment) VALUES (?,?,?)", (rid, rating, comment))
        except sqlite3.IntegrityError:
            pass

    conn.commit()
    conn.close()
    print("Sample data inserted. Database ready at database.db")

if __name__ == "__main__":
    init_db()
