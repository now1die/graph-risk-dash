from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="VFSim Backend",
    description="Backend API for VFSim",
    version="0.1.0"
)

# Allow the React frontend to communicate with the backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    return {
        "message": "VFSim backend is running"
    }


@app.get("/api/status")
def get_status():
    return {
        "backend": "online",
        "mode": "live",
        "gnn": "not_loaded"
    }
