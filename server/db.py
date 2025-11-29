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


def create_user(usename:str,password:str)
       

if __name__ == "__main__":
    
    print("DB file path:", DB_FILE)

    conn = get_connection()
    print("Connection opened successfully!")
    conn.close()
    print("Connection closed.")
