from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


@dataclass
class Transaction:
    txn_id: str
    op_type: str
    inodes_touched: list[int]
    timestamp: str
    metadata: dict[str, Any] = field(default_factory=dict)


class TransactionLog:
    def __init__(self):
        self.transactions: list[Transaction] = []

    def add(self, transaction: Transaction):
        self.transactions.append(transaction)

    def get_all(self):
        return self.transactions

    def get_by_id(self, txn_id: str):
        for transaction in self.transactions:
            if transaction.txn_id == txn_id:
                return transaction

        return None
