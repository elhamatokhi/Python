from pydantic import BaseModel

# Base user schema
class User(BaseModel):
    id: int
    name: str
    email: str

# Schema for user creation
class UserCreate(BaseModel):
    name: str
    email: str
