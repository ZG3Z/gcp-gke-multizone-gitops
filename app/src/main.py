from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
import socket
import os

from .database import get_db, init_db, Item 
from .secrets import get_secret  

app = FastAPI()

@app.on_event("startup")
def startup():
    try:
        db_password = get_secret("db-password")
        os.environ["DB_PASSWORD"] = db_password
        init_db()

    except Exception as e:
        raise

def get_zone():
    node_name = os.getenv("NODE_NAME", "")
    if not node_name:
        return "unknown"
    
    try:
        from kubernetes import client, config
        config.load_incluster_config()
        v1 = client.CoreV1Api()
        node = v1.read_node(node_name)
        return node.metadata.labels.get("topology.kubernetes.io/zone", "unknown")
    except:
        for z in ["b", "c", "d"]:
            if f"us-east1-{z}" in node_name:
                return f"us-east1-{z}"
        return "unknown"

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/")
def root():
    return {
        "message": "FastAPI + Cloud SQL + Secret Manager + GKE",
        "hostname": socket.gethostname(),
        "pod": os.getenv("POD_NAME", "unknown"),
        "zone": get_zone(),
        "database": "postgresql",
    }

@app.get("/api/data")
def list_data(db: Session = Depends(get_db)):
    items = db.query(Item).all()
    return {
        "count": len(items),
        "items": [{
            "id": i.id,
            "name": i.name,
            "value": i.value,
            "created_at": i.created_at.isoformat(),
        } for i in items],
    }

@app.post("/api/data")
def create_data(item: dict, db: Session = Depends(get_db)):
    item_id = item.get("id")
    if not item_id:
        raise HTTPException(400, "id required")
    
    if db.query(Item).filter(Item.id == item_id).first():
        raise HTTPException(409, "Item exists")
    
    db_item = Item(
        id=item_id,
        name=item.get("name", ""),
        value=item.get("value"),
        description=item.get("description"),
        created_by=socket.gethostname(),
    )
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    
    return {"message": "created", "item": {"id": db_item.id, "name": db_item.name}}

@app.get("/api/data/{item_id}")
def get_data(item_id: str, db: Session = Depends(get_db)):
    item = db.query(Item).filter(Item.id == item_id).first()
    if not item:
        raise HTTPException(404, "Not found")
    return {
        "id": item.id,
        "name": item.name,
        "value": item.value,
        "created_at": item.created_at.isoformat(),
    }

@app.delete("/api/data/{item_id}")
def delete_data(item_id: str, db: Session = Depends(get_db)):
    item = db.query(Item).filter(Item.id == item_id).first()
    if not item:
        raise HTTPException(404, "Not found")
    db.delete(item)
    db.commit()
    return {"message": "deleted"}