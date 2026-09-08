from datetime import datetime
import uuid

from .models import Inode
from .transaction import Transaction, TransactionLog


class VirtualFileSystem:

    def __init__(self):
        self.inodes: dict[str, Inode] = {}
        self.next_inode_id = 1

        self.transaction_log = TransactionLog()

        # Create root directory
        self._add_inode("/", "directory")

    def _add_inode(self, path: str, inode_type: str = "file"):
        inode = Inode(
            inode_id=self.next_inode_id,
            path=path,
            inode_type=inode_type
        )

        self.inodes[path] = inode
        self.next_inode_id += 1

        return inode

    def _create_transaction(
        self,
        op_type: str,
        inode_ids: list[int],
        metadata: dict
    ):
        transaction = Transaction(
            txn_id=f"tx-{uuid.uuid4().hex[:8]}",
            op_type=op_type,
            inodes_touched=inode_ids,
            timestamp=datetime.utcnow().isoformat(),
            metadata=metadata
        )

        self.transaction_log.add(transaction)

        return transaction

    def create(self, path: str, inode_type: str = "file"):

        if path in self.inodes:
            raise ValueError("Path already exists")

        inode = self._add_inode(path, inode_type)

        inode.dirty = True

        return self._create_transaction(
            "create",
            [inode.inode_id],
            {
                "path": path,
                "inode_type": inode_type
            }
        )

    def write(self, path: str, size: int):

        if path not in self.inodes:
            raise ValueError("File does not exist")

        inode = self.inodes[path]

        if inode.inode_type != "file":
            raise ValueError("Cannot write to a directory")

        inode.size += size
        inode.dirty = True

        return self._create_transaction(
            "write",
            [inode.inode_id],
            {
                "path": path,
                "bytes_written": size
            }
        )

    def unlink(self, path: str):

        if path not in self.inodes:
            raise ValueError("Path does not exist")

        inode = self.inodes[path]

        del self.inodes[path]

        return self._create_transaction(
            "unlink",
            [inode.inode_id],
            {
                "path": path
            }
        )

    def rename(self, old_path: str, new_path: str):

        if old_path not in self.inodes:
            raise ValueError("Source path does not exist")

        if new_path in self.inodes:
            raise ValueError("Destination path already exists")

        inode = self.inodes.pop(old_path)

        inode.path = new_path
        inode.dirty = True

        self.inodes[new_path] = inode

        return self._create_transaction(
            "rename",
            [inode.inode_id],
            {
                "old_path": old_path,
                "new_path": new_path
            }
        )

    def get_inode(self, path: str):

        return self.inodes.get(path)

    def get_all_inodes(self):

        return list(self.inodes.values())

    def get_transactions(self):

        return self.transaction_log.get_all()
