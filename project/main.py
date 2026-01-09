from fastapi import FastAPI

app = FastAPI()
# Root endpoint
@app.get('/')
def root():
    return {"message":"Hello FastApI"}

# Path parameter
@app.get("/users/{user_id}")
def get_user(user_id:int):
    return {"user_id":user_id}

@app.get("/search")
def search(q: str):
    return {"query": q}