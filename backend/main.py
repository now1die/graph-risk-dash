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
@app.get("/api/transactions")
def get_transactions():
    return {
        "transactions": [
            {
                "id": "tx-demo-001",
                "operation": "write",
                "status": "committed",
                "risk_score": 0.23
            },
            {
                "id": "tx-demo-002",
                "operation": "rename",
                "status": "committed",
                "risk_score": 0.71
            },
            {
                "id": "tx-demo-003",
                "operation": "unlink",
                "status": "in-flight",
                "risk_score": 0.86
            }
        ]
    }

    transaction = transactions.get(transaction_id)

    if transaction is None:
        return {
            "error": "Transaction not found"
        }

    return transaction
