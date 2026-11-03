from datetime import datetime
from database import get_connection

def add_item(item_code, item_name, volume, username):
    """Inserts a new inventory item profile defaulting active state status to 0."""
    conn = get_connection()
    cursor = conn.cursor()
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    try:
        cursor.execute("""
            INSERT INTO items (item_code, item_name, volume, state_active, created_date, created_by)
            VALUES (?, ?, ?, 0, ?, ?)
        """, (item_code, item_name, volume, now, username))
        conn.commit()
        success, msg = True, "Item added successfully!"
    except sqlite3.IntegrityError:
        success, msg = False, "Item Code already exists!"
    conn.close()
    return success, msg

def get_active_items():
    """Retrieves standard display columns for items where state_active is 0."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT item_code, item_name, volume FROM items WHERE state_active = 0")
    items = cursor.fetchall()
    conn.close()
    return items

def get_all_active_items_detailed():
    """Fetches full database tracking fields for data extraction streams."""
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
    """Alters name/volume data while capturing user interaction logs."""
    conn = get_connection()
    cursor = conn.cursor()
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute("""
        UPDATE items 
        SET item_name = ?, volume = ?, updated_date = ?, updated_by = ?
        WHERE item_code = ? AND state_active = 0
    """, (item_name, volume, now, username, item_code))
    conn.commit()
    conn.close()

def delete_item(item_code, username):
    """Performs a safe logical deletion by setting state_active to 1."""
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
