from dataclasses import dataclass


@dataclass
class Inode:
    inode_id: int
    path: str
    inode_type: str = "file"
    size: int = 0
    link_count: int = 1
    dirty: bool = False


@dataclass
class FileHandle:
    fd: int
    inode_id: int
    path: str
    mode: str


@dataclass
class DirEntry:
    name: str
    inode_id: int
    parent_inode_id: int
