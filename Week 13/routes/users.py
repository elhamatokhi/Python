from fastapi import APIRouter, HTTPException
from schema import User, UserCreate
import json
import os

router = APIRouter()

DATA_FILE = "users.txt"

# Read users from file
def read_users():
    if not os.path.exists(DATA_FILE):
        return []
    with open(DATA_FILE, 'r') as file:
        return json.load(file)

# Write users to file
def write_users(users):
    with open(DATA_FILE,'w') as file:
        json.dump(users, file, indent=4)

# Generate next user ID
def get_next_id(users):
    return max([user["id"] for user in users], default=0) + 1

# ---------------------------
# Routes
# ---------------------------

# Create a new user
@router.post('/', response_model=User)
def create_user(user: UserCreate):
    users = read_users()
    new_user = {
        "id": get_next_id(users),
        "name": user.name,
        "email": user.email
    }
    users.append(new_user)
    write_users(users)
    return new_user

# Get all users
@router.get('/', response_model=list[User])
def get_user():
    return read_users()

# Search users by name 
@router.get('/search',response_model=list[User])
def search_users(q: str):
    users = read_users()
    results = [u for u in users if q.lower() in u["name"].lower()]
    return results

# Get user by ID 
@router.get("/{id}", response_model=User)
def get_user(id: int):
    users = read_users()
    for user in users:
        if user["id"] == id:
            return user
    raise HTTPException(status_code=404, detail="User not found")

# Update user by ID
@router.put("/{id}", response_model=User)
def update_user(id: int, updated: UserCreate):
    users = read_users()
    for user in users:
        if user["id"] == id:
            user["name"] = updated.name
            user["email"] = updated.email
            write_users(users)
            return user
    raise HTTPException(status_code=404, detail="User not found")

# Delete user by ID
@router.delete("/{id}")
def delete_user(id: int):
    users = read_users()
    for user in users:
        if user["id"] == id:
            users.remove(user)
            write_users(users)
            return {"message": "User deleted successfully"}
    raise HTTPException(status_code=404, detail="User not found")
