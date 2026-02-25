import json 
import os

class UserStore:
    """ Encapsulates user storage logic with JSON persistence."""

    def __init__(self, file_path: str):
        self.file_path = file_path
    
    def load(self):
        """Load all users from the JSON file. Return empty list if file not found."""
        if not os.path.exists(self.file_path):
            return []
        with open(self.file_path, 'r', encoding="utf-8") as f:
            return json.load(f)
    
    def save(self, users):
        """Write list of user dictionaries to file."""
        with open(self.file_path, 'w', encoding="utf-8") as f:
            json.dump(users, f, indent=4)

    def find_by_id(self, user_id: int):
        """Return a user dict by ID or None if not found."""
        users = self.load()
        for user in users:
            if user["id"] == user_id:
                return user
        return None
    
    def get_next_id(self):
        """Compute next available ID."""
        users = self.load()
        return max([u["id"] for u in users], default=0) + 1
    
    def create_user(self, user_data: dict):
        """Add a new user and persist."""
        users = self.load()
        user_data["id"] = self.get_next_id()
        users.append(user_data)
        self.save(users)
        return user_data
    
    def update_user(self, user_id:int, updated_data: dict):
        """Update a user by ID. Return updated dict or None if not found."""
        users = self.load()
        for user in users:
            if user["id"] == user_id:
                user.update(updated_data)
                self.save(users)
                return user
            return None
        
    def delete_user(self, user_id: int):
        """Delete a user by ID. Return True if deleted, False if not found."""
        users = self.load()
        for user in users:
            if user["id"] == user_id:
                users.remove(user)
                self.save(users)
                return True
            return False
