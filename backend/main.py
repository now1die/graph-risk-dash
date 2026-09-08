from vfs.filesystem import VirtualFileSystem
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="VFSim Backend",
    description="Backend API for VFSim",
    version="0.1.0"
)
vfs = VirtualFileSystem()

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


@app.get("/api/transactions/{transaction_id}")
def get_transaction(transaction_id: str):

    transactions = {
        "tx-demo-001": {
            "id": "tx-demo-001",
            "operation": "write",
            "status": "committed",
            "risk_score": 0.23,
            "operations": 2
        },

        "tx-demo-002": {
            "id": "tx-demo-002",
            "operation": "rename",
            "status": "committed",
            "risk_score": 0.71,
            "operations": 3
        },

        "tx-demo-003": {
            "id": "tx-demo-003",
            "operation": "unlink",
            "status": "in-flight",
            "risk_score": 0.86,
            "operations": 5
        }
    }

    transaction = transactions.get(transaction_id)

    if transaction is None:
        return {
            "error": "Transaction not found"
        }

    return transaction
@app.get("/api/vfs")
def get_vfs():

    return {
        "inodes": [
            {
                "inode_id": inode.inode_id,
                "path": inode.path,
                "type": inode.inode_type,
                "size": inode.size,
                "dirty": inode.dirty
            }
            for inode in vfs.get_all_inodes()
        ]
    }
@app.get("/api/vfs")
def get_vfs():
    return {
        "inodes": [
            {
                "inode_id": inode.inode_id,
                "path": inode.path,
                "type": inode.inode_type,
                "size": inode.size,
                "dirty": inode.dirty
            }
            for inode in vfs.get_all_inodes()
        ]
    }
