from fastapi import FastAPI
from routes import users

# FastAPI instance 
app = FastAPI(
    title="User Mangement API",
    description="FastAPI backend for managing users",
    version="1.0.0"
)
# Register user routes
app.include_router(users.router, prefix="/users", tags=["Users"])

# Root health check endpoint
@app.get('/')
def root():
    return {"status": "healthy", "message": "API is running"}

# Extended health endpoint
@app.get('/health')
def health():
    return {"service": "User Management API", "status": "OK"}