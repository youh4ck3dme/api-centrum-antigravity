
import bcrypt
import sqlite3
import os

db_path = "c:/Users/42195/Desktop/api-centrum-antiigravity/backend/api_centrum.db"
password_to_test = "heslo"
email_to_test = "larsenevans@proton.me"

if not os.path.exists(db_path):
    print(f"Error: Database not found at {db_path}")
    exit(1)

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

try:
    cursor.execute("SELECT hashed_password FROM users WHERE email = ?", (email_to_test,))
    row = cursor.fetchone()
    if row:
        hashed = row[0]
        if bcrypt.checkpw(password_to_test.encode('utf-8'), hashed.encode('utf-8')):
            print(f"SUCCESS: Password 'heslo' for {email_to_test} matches!")
        else:
            print(f"FAILURE: Password 'heslo' for {email_to_test} does NOT match.")
    else:
        print(f"FAILURE: User {email_to_test} not found.")
except Exception as e:
    print(f"An error occurred: {e}")
finally:
    conn.close()
