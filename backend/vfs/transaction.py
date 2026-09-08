from dataclasses import dataclass, field
from typing import Any, List, Dict


@dataclass
class Transaction:
    txn_id: str
    op_type: str
    inodes_touched: List[int]
    timestamp: str
    metadata: Dict[str, Any] = field(default_factory=dict)


class TransactionLog:

    def __init__(self):
        self.transactions: List[Transaction] = []

    def add(self, transaction: Transaction):
        self.transactions.append(transaction)

    def get_all(self):
        return self.transactions

    def get_by_id(self, txn_id: str):
        for transaction in self.transactions:
            if transaction.txn_id == txn_id:
                return transaction

        return None
