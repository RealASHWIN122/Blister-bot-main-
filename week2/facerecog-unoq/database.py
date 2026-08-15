import sqlite3
import os

DB_NAME = 'attendance.db'

def get_connection():
    return sqlite3.connect(DB_NAME)

def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    # Create the users table with new food tracking columns
    cursor.execute('DROP TABLE IF EXISTS users')
    cursor.execute('''
        CREATE TABLE users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            face_path TEXT,
            morning_before_food TEXT DEFAULT '',
            morning_after_food TEXT DEFAULT '',
            afternoon_before_food TEXT DEFAULT '',
            afternoon_after_food TEXT DEFAULT '',
            evening_before_food TEXT DEFAULT '',
            evening_after_food TEXT DEFAULT ''
        )
    ''')
    conn.commit()
    conn.close()

def add_user(name, face_path):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO users (name, face_path)
        VALUES (?, ?)
    ''', (name, face_path))
    user_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return user_id

def get_user_by_id(user_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE id = ?', (user_id,))
    user = cursor.fetchone()
    conn.close()
    return user

def get_all_users():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users')
    users = cursor.fetchall()
    conn.close()
    return users

# Initialize database when this module is loaded
init_db()
