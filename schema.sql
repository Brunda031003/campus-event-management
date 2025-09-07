PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS colleges (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS students (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT UNIQUE,
    college_id INTEGER,
    FOREIGN KEY (college_id) REFERENCES colleges(id) ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    description TEXT,
    type TEXT,
    college_id INTEGER,
    start_date TEXT,
    end_date TEXT,
    created_at TEXT DEFAULT (datetime('now')),
    FOREIGN KEY (college_id) REFERENCES colleges(id) ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS registrations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id INTEGER NOT NULL,
    event_id INTEGER NOT NULL,
    registered_at TEXT DEFAULT (datetime('now')),
    UNIQUE(student_id, event_id),
    FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE,
    FOREIGN KEY (event_id) REFERENCES events(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS attendance (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    registration_id INTEGER NOT NULL UNIQUE,
    status TEXT CHECK(status IN ('present','absent','unknown')) DEFAULT 'unknown',
    marked_at TEXT DEFAULT (datetime('now')),
    FOREIGN KEY (registration_id) REFERENCES registrations(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS feedback (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    registration_id INTEGER NOT NULL UNIQUE,
    rating INTEGER CHECK(rating >=1 AND rating <=5),
    comment TEXT,
    submitted_at TEXT DEFAULT (datetime('now')),
    FOREIGN KEY (registration_id) REFERENCES registrations(id) ON DELETE CASCADE
);
