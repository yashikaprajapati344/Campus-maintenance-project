from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import sqlite3
import pandas as pd
import os
from datetime import datetime

app = Flask(__name__, static_folder='.')
CORS(app)  # Enable Cross-Origin Resource Sharing

DB_PATH = os.path.join("data", "campus.db")

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    os.makedirs("data", exist_ok=True)
    os.makedirs("reports", exist_ok=True)
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Complaints table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS complaints (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            complaint_id TEXT UNIQUE NOT NULL,
            student_name TEXT NOT NULL,
            department TEXT NOT NULL,
            building TEXT NOT NULL,
            room_no TEXT NOT NULL,
            category TEXT NOT NULL,
            problem TEXT NOT NULL,
            priority TEXT NOT NULL,
            status TEXT DEFAULT 'Pending',
            date TEXT NOT NULL
        )
    ''')
    
    # Maintenance table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS maintenance (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            complaint_id TEXT UNIQUE NOT NULL,
            staff_name TEXT NOT NULL,
            repair_date TEXT NOT NULL,
            cost REAL NOT NULL,
            remarks TEXT NOT NULL,
            FOREIGN KEY (complaint_id) REFERENCES complaints (complaint_id)
        )
    ''')
    
    conn.commit()
    conn.close()

# Initialize DB on start
init_db()

# Serve static web frontend
@app.route("/")
def index():
    return send_from_directory(".", "index.html")

# API Route 1: Get All Complaints
@app.route("/api/tickets", methods=["GET"])
def get_tickets():
    conn = get_db_connection()
    complaints = conn.execute("SELECT * FROM complaints ORDER BY id DESC").fetchall()
    conn.close()
    
    return jsonify([dict(row) for row in complaints]), 200

# API Route 2: Register New Complaint
@app.route("/api/tickets", methods=["POST"])
def register_ticket():
    data = request.json
    
    required_fields = ['student_name', 'department', 'building', 'room_no', 'category', 'problem', 'priority']
    if not all(k in data and data[k] for k in required_fields):
        return jsonify({"error": "Missing required fields"}), 400
        
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) FROM complaints")
    count = cursor.fetchone()[0] + 1
    complaint_id = f"CMP{count:03d}"
    today_str = datetime.now().strftime("%Y-%m-%d")
    
    cursor.execute('''
        INSERT INTO complaints (complaint_id, student_name, department, building, room_no, category, problem, priority, status, date)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'Pending', ?)
    ''', (complaint_id, data['student_name'], data['department'], data['building'], 
          data['room_no'], data['category'], data['problem'], data['priority'], today_str))
    
    conn.commit()
    conn.close()
    
    return jsonify({"message": "Complaint registered successfully", "ticket_id": complaint_id}), 201

# API Route 3: Update Ticket Status
@app.route("/api/tickets/<ticket_id>/status", methods=["PUT"])
def update_status(ticket_id):
    data = request.json
    new_status = data.get("status")
    
    if new_status not in ["Pending", "In Progress", "Resolved"]:
        return jsonify({"error": "Invalid status value"}), 400
        
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE complaints SET status = ? WHERE complaint_id = ?", (new_status, ticket_id))
    updated = cursor.rowcount > 0
    conn.commit()
    conn.close()
    
    if updated:
        return jsonify({"message": f"Status for {ticket_id} updated to {new_status}"}), 200
    return jsonify({"error": "Ticket not found"}), 404

# API Route 4: Add Maintenance Record
@app.route("/api/maintenance", methods=["POST"])
def add_maintenance():
    data = request.json
    try:
        cost = float(data.get("cost", 0))
        if cost < 0:
            raise ValueError
    except ValueError:
        return jsonify({"error": "Cost must be a positive number"}), 400

    conn = get_db_connection()
    cursor = conn.cursor()
    today_str = datetime.now().strftime("%Y-%m-%d")
    
    cursor.execute('''
        INSERT OR REPLACE INTO maintenance (complaint_id, staff_name, repair_date, cost, remarks)
        VALUES (?, ?, ?, ?, ?)
    ''', (data['complaint_id'], data['staff_name'], today_str, cost, data['remarks']))
    
    conn.commit()
    conn.close()
    return jsonify({"message": "Maintenance record added successfully"}), 200

# API Route 5: Metrics & Pandas Data Analysis Report
@app.route("/api/reports/analytics", methods=["GET"])
def get_analytics():
    conn = get_db_connection()
    df_c = pd.read_sql_query("SELECT * FROM complaints", conn)
    df_m = pd.read_sql_query("SELECT * FROM maintenance", conn)
    conn.close()

    total = len(df_c)
    pending = len(df_c[df_c['status'] == 'Pending']) if not df_c.empty else 0
    progress = len(df_c[df_c['status'] == 'In Progress']) if not df_c.empty else 0
    resolved = len(df_c[df_c['status'] == 'Resolved']) if not df_c.empty else 0

    total_cost = float(df_m['cost'].sum()) if not df_m.empty else 0.0
    avg_cost = float(df_m['cost'].mean()) if not df_m.empty else 0.0

    return jsonify({
        "total_tickets": total,
        "pending": pending,
        "in_progress": progress,
        "resolved": resolved,
        "total_cost": total_cost,
        "avg_cost": avg_cost
    }), 200

if __name__ == "__main__":
    app.run(debug=True, port=5000)