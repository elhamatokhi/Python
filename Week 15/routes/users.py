from fastapi import APIRouter, HTTPException
from schema import User, UserCreate
from user_store import UserStore

router = APIRouter()

# Initialize SQLite store
store = UserStore("users.db")

# Get all users
@router.get("/", response_model=list[User])
def get_users():
    return store.load()

# Search users by name (route order matters)
@router.get("/search", response_model=list[User])
def search_users(q: str):
    users = store.load()
    return [u for u in users if q.lower() in u["name"].lower()]

# Create a new user
@router.post("/", response_model=User)
def create_user(user: UserCreate):
    return store.save(user.dict())

# Get user by ID
@router.get("/{user_id}", response_model=User)
def get_user(user_id: int):
    user = store.find_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

# Update user by ID
@router.put("/{user_id}", response_model=User)
def update_user(user_id: int, updated: UserCreate):
    if not store.update_user(user_id, updated.dict()):
        raise HTTPException(status_code=404, detail="User not found")
    return store.find_by_id(user_id)

# Delete user by ID
@router.delete("/{user_id}")
def delete_user(user_id: int):
    if not store.delete_user(user_id):
        raise HTTPException(status_code=404, detail="User not found")
    return {"message": "User deleted successfully"}