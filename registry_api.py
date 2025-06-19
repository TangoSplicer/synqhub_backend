# synqhub_backend/registry_api.py

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import json, uuid, os
from datetime import datetime

app = FastAPI()

REGISTRY_PATH = "plugin_registry.json"

# Enable CORS for local/frontend dev
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Plugin schema
class Plugin(BaseModel):
    name: str
    author: str
    description: str
    tags: list[str]
    version: str
    license: str
    signed: bool = False
    score: int = 0

def load_registry():
    if not os.path.exists(REGISTRY_PATH):
        return []
    with open(REGISTRY_PATH, "r") as f:
        return json.load(f)

def save_registry(data):
    with open(REGISTRY_PATH, "w") as f:
        json.dump(data, f, indent=2)

@app.get("/plugins")
def list_plugins():
    return load_registry()

@app.post("/publish")
def publish_plugin(plugin: Plugin):
    plugins = load_registry()
    plugin_entry = plugin.dict()
    plugin_entry["id"] = str(uuid.uuid4())
    plugin_entry["published"] = datetime.utcnow().strftime("%Y-%m-%d")
    plugins.append(plugin_entry)
    save_registry(plugins)
    return {"status": "ok", "id": plugin_entry["id"]}

@app.post("/verify")
def verify_signature(request: Request):
    # Placeholder: In real system, use SynQ's signature check logic
    return {"verified": True, "method": "Quantum-safe signature (placeholder)"}