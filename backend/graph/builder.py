import torch
from torch_geometric.data import HeteroData


def build_graph(vfs):
    """
    Convert the current VFS state into a PyTorch Geometric graph.

    Current version:
    - Creates inode nodes
    - Creates inode features
    - Does not create relationships yet
    """

    data = HeteroData()

    inodes = vfs.get_all_inodes()

    if not inodes:
        data["inode"].x = torch.empty((0, 6), dtype=torch.float)
        return data

    max_size = max(inode.size for inode in inodes)

    if max_size == 0:
        max_size = 1

    features = []

    for inode in inodes:

        is_file = 1.0 if inode.inode_type == "file" else 0.0
        is_directory = 1.0 if inode.inode_type == "directory" else 0.0

        normalized_size = inode.size / max_size

        depth = inode.path.count("/") - 1

        feature = [
            is_file,
            is_directory,
            normalized_size,
            float(inode.link_count),
            1.0 if inode.dirty else 0.0,
            float(depth)
        ]

        features.append(feature)

    data["inode"].x = torch.tensor(
        features,
        dtype=torch.float
    )

    return data
