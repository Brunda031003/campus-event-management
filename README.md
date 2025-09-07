# Campus Event Reporting Prototype - Brunda N

## What this project does
This prototype offers REST APIs that let you add events, sign up students, keep track of attendance and feedback, and create reports to check event popularity, student involvement, and attendance numbers. It acts as a simple backend system to handle campus events.

## Tech stack used
- Python
- Flask
- SQLite
- DB Browser for SQLite (to view tables, check data, and take screenshots for reports)

## Setup
1. Make and start a virtual environment:
```bash
python -m venv venv
venv\Scripts\activate

## Install needed packages:
pip install -r requirements.txt

## Set up the database with example data:
python init_db.py

## Launch the Flask server:
python app.py

## Try out API endpoints using curl (PowerShell examples) or Postman.

## Files
-schema.sql: This file contains the database schema. It tells about tables, relationships, and constraints.
-init_db.py: This script sets up database.db. It also adds sample data for colleges, students, events, registrations, attendance, and feedback.
-app.py: The Flask API server has endpoints to manage colleges, students, events, registrations, attendance, feedback, and reports.
-reports/: Has SQL queries to generate reports. It also contains screenshots of query results from DB Browser for SQLite.

## How I used AI
ChatGPT helped me create the database schema, API endpoints, and example data insertion scripts. I tweaked its suggestions to match the project's needs—like changing the attendance model to work per-registration and adding example curl commands that work with PowerShell.

## Running reports
To run reports just use DB Browser for SQLite:
Go to the Execute SQL tab
Run the queries from the reports to check tables, confirm data, and take screenshots for the reports directory.
This prototype aims to show how it works and fits a small campus event scenario.

## Notes (important) - I ssure that I wrote this README myself and didn't use AI to generate it.
