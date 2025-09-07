# Design Document - Campus Event Reporting System (Prototype)

## Overview
Build a minimal backend prototype to support event creation, student registration, attendance marking, feedback collection, and reporting.

## Data to Track
- Event creation (name, type, date, college)
- Student registration (student_id, event_id, time)
- Attendance (present/absent per registration)
- Feedback (rating 1-5, comment)

## Schema
+----------------+       +----------------+       +----------------+
|   colleges     |       |    students    |       |     events     |
+----------------+       +----------------+       +----------------+
| id (PK)        |<------| college_id (FK)|       | id (PK)        |
| name           |       | id (PK)        |<------| college_id (FK)|
+----------------+       | name           |       | name           |
                         | email          |       | description    |
                         +----------------+       | type           |
                                                  | start_date     |
                                                  | end_date       |
                                                  +----------------+
                                                         |
                                                         |
                                                         v
                                              +-------------------+
                                              |   registrations   |
                                              +-------------------+
                                              | id (PK)           |
                                              | student_id (FK)   |
                                              | event_id (FK)     |
                                              | registered_at     |
                                              +-------------------+
                                                        |
                       +--------------------------------+--------------------------------+
                       |                                                                |
                       v                                                                v
            +--------------------+                                       +--------------------+
            |    attendance      |                                       |     feedback       |
            +--------------------+                                       +--------------------+
            | id (PK)            |                                       | id (PK)            |
            | registration_id(FK)|<------------------------------------->| registration_id(FK)|
            | status             |                                       | rating             |
            | marked_at          |                                       | comment            |
            +--------------------+                                       | submitted_at       |
                                                                         +--------------------+


Tables:
- colleges(id, name)
- students(id, name, email, college_id)
- events(id, name, description, type, college_id, start_date, end_date)
- registrations(id, student_id, event_id, registered_at) [unique(student_id,event_id)]
- attendance(id, registration_id, status, marked_at) [unique(registration_id)]
- feedback(id, registration_id, rating, comment) [unique(registration_id)]

## API Endpoints (summary)
- POST /college {name}
- POST /student {name,email,college_id}
- POST /event {name,description,type,college_id,start_date,end_date}
- GET /events
- POST /register {student_id,event_id}
- POST /attendance {registration_id or student_id,event_id, status}
- POST /feedback {registration_id, rating, comment}
- GET /report/registrations[?college_id&type]
- GET /report/attendance/<event_id>
- GET /report/feedback/<event_id>
- GET /report/active-students[?top=3]

## Workflows
1. Student registration:
   - Student clicks register -> backend creates row in `registrations` if not exists.
2. Attendance:
   - On event day, admin marks attendance (by scanning or selecting) -> `attendance` row created/updated for registration.
3. Feedback:
   - After event, student submits rating -> `feedback` row created/updated.
4. Reporting:
   - Admin calls report endpoints or runs SQL queries to compute popularity, participation, attendance %.

## Assumptions & Edge Cases
- Students have unique email (optional).
- Duplicate registrations prevented by unique(student_id,event_id).
- Attendance is linked to a registration (no marking for non-registered student).
- Feedback linked to registration and only one feedback per registration (can update).
- Event IDs are globally unique; we use single DB for all colleges but filter by college_id for isolated views.
- Scale: prototype supports ~50 colleges, 500 students/college; SQLite ok for prototype but switch to Postgres for production.

## AI Assistance
Followed suggestions: I utilized AI to help brainstorm the database schema, design the API, and come up with sample queries.
Deviations: I opted to change attendance tracking to be based on pre-registration rather than per-student-event, added unique constraints for registrations and feedback, and tailored reports to fit the assignment requirements.

