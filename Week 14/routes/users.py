from fastapi import APIRouter, HTTPException
from schema import User, UserCreate
from user_store import UserStore

router = APIRouter()

# Initialize user store
store = UserStore("users.txt")

# ---------------------------
# CRUD Endpoints
# ---------------------------

# Get all users
@router.get('/', response_model=list[User])
def get_user():
    return store.load()

# Search user by name
@router.get('/search', response_model=list[User])
def search_user(q: str):
    users = store.load()
    return [u for u in users if q.lower() in u['name'].lower()]

# Create a new user
@router.get('/', response_model=User)
def create_user(user: UserCreate):
    return store.create_user(user.dict())

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
    user = store.update_user(user_id, updated.dict())
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

# Delete user by ID
@router.delete("/{user_id}")
def delete_user(user_id: int):
    if store.delete_user(user_id):
        return {"message": "User deleted successfully"}
    raise HTTPException(status_code=404, detail="User not found")