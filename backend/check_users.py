
import sqlite3
import os

db_path = "c:/Users/42195/Desktop/api-centrum-antiigravity/backend/api_centrum.db"

if not os.path.exists(db_path):
    print(f"Error: Database not found at {db_path}")
    exit(1)

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

try:
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    print(f"Tables: {tables}")

    if ('users',) in tables:
        cursor.execute("SELECT id, email, hashed_password FROM users")
        users = cursor.fetchall()
        print("Users in database:")
        for user in users:
            print(f"ID: {user[0]}, Email: {user[1]}, Hash: {user[2]}")
    else:
        print("Error: 'users' table not found.")
except Exception as e:
    print(f"An error occurred: {e}")
finally:
    conn.close()
