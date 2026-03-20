import sqlite3
import os

db_path = os.path.join('backend', 'api_centrum.db')
if not os.path.exists(db_path):
    print(f"Database {db_path} not found")
    exit(1)

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

print("--- Users ---")
try:
    cursor.execute("SELECT id, email, is_active FROM users")
    users = cursor.fetchall()
    for user in users:
        print(f"ID: {user[0]}, Email: {user[1]}, Active: {user[2]}")
except Exception as e:
    print(f"Error fetching users: {e}")

print("\n--- Recent Audit Logs (Auth) ---")
try:
    cursor.execute("SELECT id, user_id, action, detail, created_at FROM audit_logs WHERE action IN ('login', 'auth_failure') ORDER BY created_at DESC LIMIT 5")
    logs = cursor.fetchall()
    for log in logs:
        print(f"ID: {log[0]}, UserID: {log[1]}, Action: {log[2]}, Detail: {log[3]}, At: {log[4]}")
except Exception as e:
    print(f"Error fetching audit logs: {e}")

conn.close()
