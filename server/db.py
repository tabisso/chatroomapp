#Database config file for the project 
import sqlite3
from pathlib import Path
from typing import List, Dict 
from werkzeug.security import generate_password_hash, check_password_hash

#Path to this folder
BASE_DIR = Path(__file__).resolve().parent

#Path to the chat.db file
DB_FILE = BASE_DIR / "chat.db"


def get_connection():
    """
    Open a new SQLite connection.
    Each call returns a fresh connection .
    """
    
    conn = sqlite3.connect(DB_FILE)
    print(type(conn))
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """
    Create the users and messages tables if they don't exist yet.
    """

    with get_connection() as conn:
        cur = conn.cursor()

        query_for_usersTable =""" CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL UNIQUE,
                password_hash TEXT NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            );"""
        

        query_for_messagesTable= """
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                sender_username TEXT NOT NULL,
                content TEXT NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (sender_username) REFERENCES users(username)
            );
            """
        
        cur.execute(query_for_usersTable)
        cur.execute(query_for_messagesTable)
        
        conn.commit() #commiting the changes to the db

# ---------- User functions ----------


def create_user(username: str, password: str):
    """
    Create a new user with a hashed password.
    Returns True if created, False if username already exists.
    """

    password_hash = generate_password_hash(password)

    try:
        with get_connection() as conn:
            conn.execute(
                """
                INSERT INTO users (username, password_hash)
                VALUES (?, ?);
                """,
                (username, password_hash),
            )
        return True
    except sqlite3.IntegrityError:
        # UNIQUE(username) violated -> user already exists
        return False

def verify_user(username: str, password: str) -> bool:
    """
    Check if the username exists and password matches the stored hash.
    """

    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute(
            "SELECT password_hash FROM users WHERE username = ?;",
            (username,),
        )
        row = cur.fetchone()
        
        if row is None:
            return False
        
        return check_password_hash(row["password_hash"], password)


# ---------- Message functions ----------


def add_message(sender: str, content: str) -> Dict:
    """
    Insert a new message into the database and return it as a dict.
    """

    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute(
            """
            INSERT INTO messages (sender_username, content)
            VALUES (?, ?);
            """,
            (sender, content),
        )
        msg_id = cur.lastrowid

        # Fetch the inserted row to get details 
        cur.execute(
            """
            SELECT id, sender_username AS sender, content, created_at
            FROM messages
            WHERE id = ?;
            """,
            (msg_id,),
        )
        row = cur.fetchone()

    return {
        "id": row["id"],
        "sender": row["sender"],
        "content": row["content"],
        "timestamp": row["created_at"],
    }


def get_messages_after(last_id: int) ->List[Dict] :
    """
    Get all messages with id > last_id, ordered by id.
    """
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute(
            """
            SELECT id, sender_username AS sender, content, created_at
            FROM messages
            WHERE id > ?
            ORDER BY id ASC;
            """,
            (last_id,),

        )
        rows = cur.fetchall()

        messages: List[Dict] = []
        for row in rows:
            messages.append(
                {
                "id": row["id"],
                "sender": row["sender"],
                "content": row["content"],
                "timestamp": row["created_at"],
            }
            )

        return messages





if __name__ == "__main__":
    
    print("DB file path:", DB_FILE)

    conn = get_connection()
    print("Connection opened successfully!")
    conn.close()
    print("Connection closed.")
