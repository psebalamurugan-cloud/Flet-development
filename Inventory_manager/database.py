import os
import sys
import sqlite3
from datetime import datetime
from format_volume import format_unit

# -------------------------------------------------------------
# 1. Connection Logic (from connection.py)
# -------------------------------------------------------------
DB_NAME = "stocks.db"

def get_connection():
    return sqlite3.connect(DB_NAME)

def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS itemcode(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            s_no INTEGER NOT NULL, 
            item_code TEXT UNIQUE NOT NULL           
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            item_code TEXT UNIQUE NOT NULL,
            item_name TEXT NOT NULL,
            volume TEXT NOT NULL,
            state_active INTEGER NOT NULL,
            created_date TEXT NOT NULL,
            updated_date TEXT,
            created_by TEXT NOT NULL,
            updated_by TEXT
        )
    """)
    try:
        #cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", ("admin", "admin123"))
        conn.commit()
    except sqlite3.IntegrityError:
        pass
    conn.close()

# -------------------------------------------------------------
# 2. Users Logic (from users.py)
# -------------------------------------------------------------
def validate_user(username, password):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, password))
    user = cursor.fetchone()
    conn.close()
    return user is not None

# -------------------------------------------------------------
# 3. Items Logic (from items.py)
# -------------------------------------------------------------
def add_item(item_code, item_name, volume, username):
    conn = get_connection()
    cursor = conn.cursor()
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    auto_item_code = generate_next_item_code()
    vol = format_unit(volume)
    try:
        cursor.execute("""
            INSERT INTO items (item_code, item_name, volume, state_active, created_date, updated_date, created_by, updated_by)
            VALUES (?, ?, ?, 0, ?, ?, ?, ?)
        """, (auto_item_code, item_name.upper(), vol, now, now, username, username))
        conn.commit()
        success, msg = True, "Item added successfully!"
    except sqlite3.IntegrityError:
        success, msg = False, "Item Code already exists!"
    conn.commit()
    conn.close()
    return success, msg

def get_active_items():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT item_code, item_name, volume FROM items WHERE state_active = 0")
    items = cursor.fetchall()    
    conn.close()
    return items

def get_all_active_items_detailed():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT item_code, item_name, volume, state_active, created_date, created_by, updated_date, updated_by 
        FROM items WHERE state_active = 0
    """)
    items = cursor.fetchall()
    conn.close()
    return items

def update_item(item_code, item_name, volume, username):
    conn = get_connection()
    cursor = conn.cursor()
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    vol = format_unit(volume)
    cursor.execute("""
        UPDATE items 
        SET item_name = ?, volume = ?, updated_date = ?, updated_by = ?
        WHERE item_code = ? AND state_active = 0
    """, (item_name.upper(), vol, now, username, item_code))
    conn.commit()
    conn.close()

def delete_item(item_code, username):
    conn = get_connection()
    cursor = conn.cursor()
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute("""
        UPDATE items 
        SET state_active = 1, updated_date = ?, updated_by = ?
        WHERE item_code = ?
    """, (now, username, item_code))
    conn.commit()
    conn.close()

import re
import sqlite3


def generate_next_item_code():
    # Connect to the database
    conn = get_connection()
    cursor = conn.cursor()

    try:
        # 1. Fetch the last generated item code from the table
        cursor.execute(
            "SELECT item_code FROM itemcode ORDER BY id DESC LIMIT 1"
        )
        row = cursor.fetchone()
        #print(row)  # Output: AA0001
        if row is None:
            # First time setup: If table is empty, start with the baseline
            next_code = "AA0001"
            cursor.execute("INSERT INTO itemcode (s_no, item_code) VALUES (1, ?)", (next_code,))
            conn.commit()
        else:
            last_code = row[0]

            # 2. Separate the prefix (AA) from the numeric digits (0001) using regex
            match = re.match(r"([A-Za-z]+)(\d+)", last_code)
            if not match:
                raise ValueError(
                    f"Invalid item code format in database: {last_code}"
                )
            prefix = match.group(1)  # Extracts "AA"
            number_str = match.group(2)  # Extracts "0001"
            padding_length = len(number_str)  # Remembers the number of digits (4)

            # 3. Increment the numeric part by 1
            next_number = int(number_str) + 1

            # 4. Format it back with leading zeros (e.g., 2 becomes "0002")
            next_code = f"{prefix}{next_number:0{padding_length}d}"

            cursor.execute("""
                    UPDATE itemcode 
                    SET item_code = ?
                    WHERE s_no = ?
                """, (next_code, 1))       
            conn.commit()
        return next_code

    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()

#init_db()
# 2. Test consecutive calls to the function
#print(generate_next_item_code())  # Output: AA0001
#print(generate_next_item_code())  # Output: AA0002
#print(generate_next_item_code())  # Output: AA0003


