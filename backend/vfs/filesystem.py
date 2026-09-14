from datetime import datetime
import uuid
from typing import Dict, List

from .models import Inode, DirEntry
from .transaction import Transaction, TransactionLog


class VirtualFileSystem:

    def __init__(self):
        self.inodes: Dict[str, Inode] = {}
        self.next_inode_id = 1

        # Store directory-entry relationships
        self.dirents: Dict[str, DirEntry] = {}

        self.transaction_log = TransactionLog()

        # Create root directory
        self._add_inode("/", "directory")

    def _add_inode(
        self,
        path: str,
        inode_type: str = "file"
    ):
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
        inode_ids: List[int],
        metadata: Dict
    ):
        transaction = Transaction(
            txn_id="tx-" + uuid.uuid4().hex[:8],
            op_type=op_type,
            inodes_touched=inode_ids,
            timestamp=datetime.utcnow().isoformat(),
            metadata=metadata
        )

        self.transaction_log.add(transaction)

        return transaction

    def create(
        self,
        path: str,
        inode_type: str = "file"
    ):

        if path in self.inodes:
            raise ValueError("Path already exists")

        if path == "/":
            raise ValueError("Root already exists")

        # Find parent directory
        parent_path = path.rsplit("/", 1)[0]

        if parent_path == "":
            parent_path = "/"

        if parent_path not in self.inodes:
            raise ValueError("Parent directory does not exist")

        parent_inode = self.inodes[parent_path]

        if parent_inode.inode_type != "directory":
            raise ValueError("Parent is not a directory")

        # Create the inode
        inode = self._add_inode(path, inode_type)

        inode.dirty = True

        # Create directory entry
        name = path.rsplit("/", 1)[-1]

        dirent = DirEntry(
            name=name,
            inode_id=inode.inode_id,
            parent_inode_id=parent_inode.inode_id
        )

        self.dirents[path] = dirent

        return self._create_transaction(
            "create",
            [parent_inode.inode_id, inode.inode_id],
            {
                "path": path,
                "inode_type": inode_type,
                "parent_path": parent_path,
                "name": name
            }
        )

    def write(
        self,
        path: str,
        size: int
    ):

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

        if path == "/":
            raise ValueError("Cannot unlink root directory")

        inode = self.inodes[path]

        # Remove the inode
        del self.inodes[path]

        # Remove its directory entry
        if path in self.dirents:
            del self.dirents[path]

        return self._create_transaction(
            "unlink",
            [inode.inode_id],
            {
                "path": path
            }
        )

    def rename(
        self,
        old_path: str,
        new_path: str
    ):

        if old_path not in self.inodes:
            raise ValueError("Source path does not exist")

        if new_path in self.inodes:
            raise ValueError("Destination path already exists")

        if old_path == "/":
            raise ValueError("Cannot rename root directory")

        # Find destination parent directory
        new_parent_path = new_path.rsplit("/", 1)[0]

        if new_parent_path == "":
            new_parent_path = "/"

        if new_parent_path not in self.inodes:
            raise ValueError("Destination parent directory does not exist")

        new_parent_inode = self.inodes[new_parent_path]

        if new_parent_inode.inode_type != "directory":
            raise ValueError("Destination parent is not a directory")

        inode = self.inodes.pop(old_path)

        # Update inode path
        inode.path = new_path
        inode.dirty = True

        self.inodes[new_path] = inode

        # Update directory entry
        if old_path in self.dirents:
            dirent = self.dirents.pop(old_path)

            dirent.name = new_path.rsplit("/", 1)[-1]
            dirent.parent_inode_id = new_parent_inode.inode_id

            self.dirents[new_path] = dirent

        return self._create_transaction(
            "rename",
            [inode.inode_id, new_parent_inode.inode_id],
            {
                "old_path": old_path,
                "new_path": new_path,
                "new_parent_path": new_parent_path
            }
        )

    def get_inode(self, path: str):

        return self.inodes.get(path)

    def get_all_inodes(self):

        return list(self.inodes.values())

    def get_all_dirents(self):

        return list(self.dirents.values())

    def get_transactions(self):

        return self.transaction_log.get_all()
