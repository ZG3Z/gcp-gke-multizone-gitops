from fastapi import FastAPI
from datetime import datetime
import socket
import os

app = FastAPI()

data = {}

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/")
def root():
    return {
        "message": "FastAPI on GKE",
        "hostname": socket.gethostname(),
        "pod": os.getenv("POD_NAME", "unknown"),
        "zone": os.getenv("ZONE", "unknown"),
    }

@app.get("/api/data")
def list_data():
    return {"items": list(data.values())}

@app.post("/api/data")
def create_data(item: dict):
    item_id = item.get("id")
    if not item_id:
        return {"error": "id required"}, 400
    
    data[item_id] = item
    return {"created": item}

@app.get("/api/data/{item_id}")
def get_data(item_id: str):
    return data.get(item_id, {"error": "not found"})

@app.delete("/api/data/{item_id}")
def delete_data(item_id: str):
    if item_id in data:
        del data[item_id]
        return {"deleted": item_id}
    return {"error": "not found"}