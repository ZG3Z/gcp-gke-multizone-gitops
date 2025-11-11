from fastapi import FastAPI
from datetime import datetime
import socket
import os

app = FastAPI()

data = {}

zone_cache = None

def get_zone():
    global zone_cache
    
    if zone_cache:
        return zone_cache
    
    node_name = os.getenv("NODE_NAME")
    if not node_name:
        return "unknown"
    
    try:
        from kubernetes import client, config
        
        config.load_incluster_config()
        
        v1 = client.CoreV1Api()
        node = v1.read_node(node_name)
        
        zone = node.metadata.labels.get("topology.kubernetes.io/zone", "unknown")
        
        zone_cache = zone
        return zone
    except Exception as e:
        if "us-east1-b" in node_name:
            return "us-east1-b"
        elif "us-east1-c" in node_name:
            return "us-east1-c"
        elif "us-east1-d" in node_name:
            return "us-east1-d"
        return f"error:{str(e)}"

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/")
def root():
    return {
        "message": "FastAPI on GKE",
        "hostname": socket.gethostname(),
        "pod": os.getenv("POD_NAME", "unknown"),
        "node": os.getenv("NODE_NAME", "unknown"),
        "zone": get_zone(),
        "version": "auto-deployed"
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