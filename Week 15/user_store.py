import sqlite3

class UserStore:
    """Handles user persistence using SQLite."""

    def __init__(self, db_path: str):
        self.db_path = db_path
        self.init_db()
    
    def init_db(self):
        """Create users table if it doesn't exist."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS users(
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    email TEXT NOT NULL
                )
            """
        )
        conn.commit()
        conn.close()
    
    def load(self):
        """Return all users as a list of dictionaries."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, email FROM users")
        rows = cursor.fetchall()
        conn.close()
        return [{"id": r[0], "name": r[1],  "email": r[2]} for r in rows]
    
    def save(self, user_data: dict):
        """Insert a new user into the database."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO users (name, email) VALUES (?, ?)",
            (user_data["name"], user_data["email"])
        )
        conn.commit()
        user_id = cursor.lastrowid
        conn.close()
        return {**user_data, "id": user_id}
    
    def find_by_id(self, user_id: int):
        """Find a user by ID or return None."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, name, email FROM users WHERE id = ?",
            (user_id,)
        )
        row = cursor.fetchone()
        conn.close()
        if row:
            return {"id": row[0], "name": row[1], "email": row[2]}
        return None
    
    def update_user(self, user_id: int, updated_data: dict):
        """Update user fields by ID."""
        conn =sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE users SET name = ?, email = ? WHERE id = ?",
            (updated_data["name"], u[updated_data["email"], user_id])
        )
        conn.commit()
        updated = cursor.rowcount
        conn.close()
        return updated > 0
    
    def delete_user(self, user_id: int):
        """Delete a user by ID."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM users WHERE id = ?", (user_id,))
        conn.commit()
        deleted = cursor.rowcount
        conn.close()
        return deleted > 0