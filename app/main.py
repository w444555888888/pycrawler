from fastapi import FastAPI
from app.api import hotels

app = FastAPI()

app.include_router(hotels.router, prefix="/api/v1/hotels")

@app.get("/")
def root():
    return {"message": "FastAPI backend ready"}
