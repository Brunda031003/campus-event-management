from flask import Flask, g, request, jsonify
import sqlite3
from pathlib import Path
from datetime import datetime

DB_PATH = Path('database.db')
app = Flask(__name__)

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = sqlite3.connect(DB_PATH)
        db.row_factory = sqlite3.Row
        db.execute("PRAGMA foreign_keys = ON;")
        g._database = db
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

def row_to_dict(r):
    return dict(r) if r is not None else None

# --- Helper endpoints for creating basic entities (used during testing) ---
@app.route('/college', methods=['POST'])
def create_college():
    data = request.json or {}
    name = data.get('name')
    if not name:
        return jsonify({"error":"name required"}), 400
    db = get_db()
    try:
        cur = db.execute("INSERT INTO colleges (name) VALUES (?)", (name,))
        db.commit()
        return jsonify({"message":"college created", "college_id": cur.lastrowid}), 201
    except sqlite3.IntegrityError:
        return jsonify({"error":"college already exists"}), 400

@app.route('/student', methods=['POST'])
def create_student():
    data = request.json or {}
    name = data.get('name')
    email = data.get('email')
    college_id = data.get('college_id')
    if not name:
        return jsonify({"error":"name required"}), 400
    db = get_db()
    try:
        cur = db.execute("INSERT INTO students (name,email,college_id) VALUES (?,?,?)", (name,email,college_id))
        db.commit()
        return jsonify({"message":"student created", "student_id": cur.lastrowid}), 201
    except sqlite3.IntegrityError as e:
        return jsonify({"error":"integrity error", "detail": str(e)}), 400

@app.route('/event', methods=['POST'])
def create_event():
    data = request.json or {}
    name = data.get('name')
    description = data.get('description')
    type_ = data.get('type')
    college_id = data.get('college_id')
    start_date = data.get('start_date')
    end_date = data.get('end_date')
    if not name:
        return jsonify({"error":"name required"}), 400
    db = get_db()
    cur = db.execute(
        "INSERT INTO events (name,description,type,college_id,start_date,end_date) VALUES (?,?,?,?,?)",
        (name,description,type_,college_id,start_date,end_date)
    )
    db.commit()
    return jsonify({"message":"event created","event_id": cur.lastrowid}), 201

@app.route('/events', methods=['GET'])
def list_events():
    college_id = request.args.get('college_id')
    type_filter = request.args.get('type')
    sql = "SELECT e.*, c.name as college_name FROM events e LEFT JOIN colleges c ON e.college_id = c.id WHERE 1=1"
    params = []
    if college_id:
        sql += " AND e.college_id = ?"
        params.append(college_id)
    if type_filter:
        sql += " AND e.type = ?"
        params.append(type_filter)
    db = get_db()
    cur = db.execute(sql, params)
    rows = [row_to_dict(r) for r in cur.fetchall()]
    return jsonify(rows)

# --- Registration ---
@app.route('/register', methods=['POST'])
def register_student():
    data = request.json or {}
    student_id = data.get('student_id')
    event_id = data.get('event_id')
    if not student_id or not event_id:
        return jsonify({"error":"student_id and event_id required"}), 400
    db = get_db()
    # Check if already registered
    cur = db.execute("SELECT id FROM registrations WHERE student_id = ? AND event_id = ?", (student_id, event_id))
    if cur.fetchone():
        return jsonify({"message":"already registered"}), 200
    try:
        cur = db.execute("INSERT INTO registrations (student_id,event_id) VALUES (?,?)", (student_id,event_id))
        db.commit()
        return jsonify({"message":"registered","registration_id": cur.lastrowid}), 201
    except sqlite3.IntegrityError as e:
        return jsonify({"error":"could not register","detail": str(e)}), 400

# --- Attendance: accept registration_id or (student_id & event_id) ---
@app.route('/attendance', methods=['POST'])
def mark_attendance():
    data = request.json or {}
    registration_id = data.get('registration_id')
    student_id = data.get('student_id')
    event_id = data.get('event_id')
    status = data.get('status', 'present')
    if not registration_id and not (student_id and event_id):
        return jsonify({"error":"provide registration_id or (student_id and event_id)"}), 400
    db = get_db()
    if not registration_id:
        cur = db.execute("SELECT id FROM registrations WHERE student_id=? AND event_id=?", (student_id,event_id))
        row = cur.fetchone()
        if not row:
            return jsonify({"error":"registration not found"}), 404
        registration_id = row['id']
    # Upsert attendance 
    try:
        cur = db.execute("INSERT INTO attendance (registration_id,status) VALUES (?,?)", (registration_id,status))
        db.commit()
        return jsonify({"message":"attendance marked","attendance_id": cur.lastrowid}), 201
    except sqlite3.IntegrityError:
        # already exists -> update
        db.execute("UPDATE attendance SET status=?, marked_at=datetime('now') WHERE registration_id=?", (status, registration_id))
        db.commit()
        return jsonify({"message":"attendance updated"}), 200

# --- Feedback: rating 1-5 ---
@app.route('/feedback', methods=['POST'])
def submit_feedback():
    data = request.json or {}
    registration_id = data.get('registration_id')
    rating = data.get('rating')
    comment = data.get('comment', '')
    if not registration_id or rating is None:
        return jsonify({"error":"registration_id and rating required"}), 400
    if not (1 <= int(rating) <= 5):
        return jsonify({"error":"rating must be between 1 and 5"}), 400
    db = get_db()
    try:
        cur = db.execute("INSERT INTO feedback (registration_id,rating,comment) VALUES (?,?,?)", (registration_id, rating, comment))
        db.commit()
        return jsonify({"message":"feedback saved","feedback_id": cur.lastrowid}), 201
    except sqlite3.IntegrityError:
        # if feedback exists, update it
        db.execute("UPDATE feedback SET rating=?, comment=?, submitted_at=datetime('now') WHERE registration_id=?", (rating, comment, registration_id))
        db.commit()
        return jsonify({"message":"feedback updated"}), 200

# --- Reports ---
@app.route('/report/registrations', methods=['GET'])
def report_registrations():
    # Optional filters
    college_id = request.args.get('college_id')
    event_type = request.args.get('type')
    db = get_db()
    sql = """
    SELECT e.id as event_id, e.name as event_name, e.type as event_type, c.name as college_name,
           COUNT(r.id) as total_registrations
    FROM events e
    LEFT JOIN colleges c ON e.college_id = c.id
    LEFT JOIN registrations r ON e.id = r.event_id
    WHERE 1=1
    """
    params = []
    if college_id:
        sql += " AND e.college_id = ?"
        params.append(college_id)
    if event_type:
        sql += " AND e.type = ?"
        params.append(event_type)
    sql += " GROUP BY e.id ORDER BY total_registrations DESC"
    cur = db.execute(sql, params)
    rows = [row_to_dict(r) for r in cur.fetchall()]
    return jsonify(rows)

@app.route('/report/attendance/<int:event_id>', methods=['GET'])
def report_attendance(event_id):
    db = get_db()
    # total registered
    cur = db.execute("SELECT COUNT(*) as cnt FROM registrations WHERE event_id = ?", (event_id,))
    total_registered = cur.fetchone()['cnt']
    # total attended (present)
    cur = db.execute("""
        SELECT COUNT(a.id) as cnt
        FROM attendance a
        JOIN registrations r ON a.registration_id = r.id
        WHERE r.event_id = ? AND a.status = 'present'
    """, (event_id,))
    total_attended = cur.fetchone()['cnt']
    attendance_pct = (total_attended / total_registered * 100) if total_registered else 0
    return jsonify({
        "event_id": event_id,
        "total_registered": total_registered,
        "total_attended": total_attended,
        "attendance_percentage": round(attendance_pct,2)
    })

@app.route('/report/feedback/<int:event_id>', methods=['GET'])
def report_feedback(event_id):
    db = get_db()
    cur = db.execute("""
        SELECT AVG(f.rating) as avg_rating, COUNT(f.id) as count_feedback
        FROM feedback f
        JOIN registrations r ON f.registration_id = r.id
        WHERE r.event_id = ?
    """, (event_id,))
    row = cur.fetchone()
    avg_rating = row['avg_rating'] if row['avg_rating'] is not None else 0
    return jsonify({
        "event_id": event_id,
        "average_feedback": round(avg_rating,2),
        "count_feedback": row['count_feedback']
    })

@app.route('/report/active-students', methods=['GET'])
def report_active_students():
    top_n = int(request.args.get('top', 3))
    db = get_db()
    cur = db.execute("""
        SELECT s.id as student_id, s.name as student_name, COALESCE(SUM(CASE WHEN a.status='present' THEN 1 ELSE 0 END),0) as attended_count
        FROM students s
        LEFT JOIN registrations r ON s.id = r.student_id
        LEFT JOIN attendance a ON r.id = a.registration_id
        GROUP BY s.id
        ORDER BY attended_count DESC
        LIMIT ?
    """, (top_n,))
    rows = [row_to_dict(r) for r in cur.fetchall()]
    return jsonify(rows)

if __name__ == "__main__":
    if not DB_PATH.exists():
        print("database.db not found. Run init_db.py first to create and populate the database.")
    app.run(debug=True, host='0.0.0.0', port=5000)
