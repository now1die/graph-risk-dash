import torch
from torch_geometric.data import HeteroData


def build_graph(vfs):
    """
    Convert the current VFS state into a PyTorch Geometric
    heterogeneous graph.

    Current graph contains:
    - inode nodes
    - dirent nodes
    - contains edges
    - links edges
    """

    data = HeteroData()

    inodes = vfs.get_all_inodes()
    dirents = vfs.get_all_dirents()

    # ---------------------------------------------------------
    # INODE NODES
    # ---------------------------------------------------------

    if not inodes:
        data["inode"].x = torch.empty((0, 6), dtype=torch.float)
    else:

        max_size = max(inode.size for inode in inodes)

        if max_size == 0:
            max_size = 1

        inode_features = []

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

            inode_features.append(feature)

        data["inode"].x = torch.tensor(
            inode_features,
            dtype=torch.float
        )

    # ---------------------------------------------------------
    # DIRENT NODES
    # ---------------------------------------------------------

    if not dirents:
        data["dirent"].x = torch.empty((0, 1), dtype=torch.float)
    else:

        dirent_features = []

        for dirent in dirents:

            name_length = len(dirent.name)

            dirent_features.append([
                float(name_length)
            ])

        data["dirent"].x = torch.tensor(
            dirent_features,
            dtype=torch.float
        )

    # ---------------------------------------------------------
    # CONTAINS EDGES
    # ---------------------------------------------------------

    if dirents:

        source_nodes = []
        target_nodes = []

        inode_id_to_index = {
            inode.inode_id: index
            for index, inode in enumerate(inodes)
        }

        for dirent_index, dirent in enumerate(dirents):

            target_inode_index = inode_id_to_index[
                dirent.inode_id
            ]

            source_nodes.append(dirent_index)
            target_nodes.append(target_inode_index)

        data["dirent", "contains", "inode"].edge_index = torch.tensor(
            [
                source_nodes,
                target_nodes
            ],
            dtype=torch.long
        )

    # ---------------------------------------------------------
    # LINKS EDGES
    # ---------------------------------------------------------

    inode_id_to_index = {
        inode.inode_id: index
        for index, inode in enumerate(inodes)
    }

    paths_by_inode = {}

    for dirent in dirents:

        inode_id = dirent.inode_id

        if inode_id not in paths_by_inode:
            paths_by_inode[inode_id] = []

        paths_by_inode[inode_id].append(dirent)

    link_sources = []
    link_targets = []

    for inode_id, inode_dirents in paths_by_inode.items():

        if len(inode_dirents) > 1:

            inode_index = inode_id_to_index[inode_id]

            for _ in range(len(inode_dirents) - 1):

                link_sources.append(inode_index)
                link_targets.append(inode_index)

    if link_sources:

        data["inode", "links", "inode"].edge_index = torch.tensor(
            [
                link_sources,
                link_targets
            ],
            dtype=torch.long
        )

    return data
