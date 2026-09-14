import torch
from torch_geometric.data import HeteroData


def build_graph(vfs):
    """
    Convert the current VFS state into a PyTorch Geometric
    heterogeneous graph.

    Node types:
    - inode
    - dirent
    - fd

    Relations:
    - inode -> dirent : contains
    - dirent -> inode : points_to
    - inode -> inode  : links
    - fd -> inode     : open_by
    - inode -> fd     : opened_by
    - inode -> inode  : renames
    """

    data = HeteroData()

    inodes = vfs.get_all_inodes()
    dirents = vfs.get_all_dirents()
    file_handles = list(vfs.file_handles.values())
    rename_history = vfs.get_rename_history()

    # =================================================
    # INODE NODES
    # =================================================

    if not inodes:

        data["inode"].x = torch.empty(
            (0, 6),
            dtype=torch.float
        )

    else:

        max_size = max(
            inode.size
            for inode in inodes
        )

        if max_size == 0:
            max_size = 1

        inode_features = []

        for inode in inodes:

            is_file = (
                1.0
                if inode.inode_type == "file"
                else 0.0
            )

            is_directory = (
                1.0
                if inode.inode_type == "directory"
                else 0.0
            )

            normalized_size = (
                inode.size / max_size
            )

            depth = (
                inode.path.count("/")
                - 1
            )

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

    inode_id_to_index = {
        inode.inode_id: index
        for index, inode in enumerate(inodes)
    }

    # =================================================
    # DIRENT NODES
    # =================================================

    if not dirents:

        data["dirent"].x = torch.empty(
            (0, 1),
            dtype=torch.float
        )

    else:

        dirent_features = []

        for dirent in dirents:

            name_length = len(
                dirent.name
            )

            dirent_features.append(
                [float(name_length)]
            )

        data["dirent"].x = torch.tensor(
            dirent_features,
            dtype=torch.float
        )

    # =================================================
    # INODE -> DIRENT
    # =================================================

    if dirents:

        source_nodes = []
        target_nodes = []

        for dirent_index, dirent in enumerate(
            dirents
        ):

            parent_inode_index = (
                inode_id_to_index[
                    dirent.parent_inode_id
                ]
            )

            source_nodes.append(
                parent_inode_index
            )

            target_nodes.append(
                dirent_index
            )

        data[
            "inode",
            "contains",
            "dirent"
        ].edge_index = torch.tensor(
            [source_nodes, target_nodes],
            dtype=torch.long
        )

    # =================================================
    # DIRENT -> INODE
    # =================================================

    if dirents:

        source_nodes = []
        target_nodes = []

        for dirent_index, dirent in enumerate(
            dirents
        ):

            target_inode_index = (
                inode_id_to_index[
                    dirent.inode_id
                ]
            )

            source_nodes.append(
                dirent_index
            )

            target_nodes.append(
                target_inode_index
            )

        data[
            "dirent",
            "points_to",
            "inode"
        ].edge_index = torch.tensor(
            [source_nodes, target_nodes],
            dtype=torch.long
        )

    # =================================================
    # HARD LINKS
    # =================================================

    paths_by_inode = {}

    for dirent in dirents:

        inode_id = dirent.inode_id

        if inode_id not in paths_by_inode:
            paths_by_inode[inode_id] = []

        paths_by_inode[inode_id].append(
            dirent
        )

    link_sources = []
    link_targets = []

    for inode_id, inode_dirents in (
        paths_by_inode.items()
    ):

        if len(inode_dirents) > 1:

            inode_index = (
                inode_id_to_index[inode_id]
            )

            for _ in range(
                len(inode_dirents) - 1
            ):

                link_sources.append(
                    inode_index
                )

                link_targets.append(
                    inode_index
                )

    if link_sources:

        data[
            "inode",
            "links",
            "inode"
        ].edge_index = torch.tensor(
            [link_sources, link_targets],
            dtype=torch.long
        )

    # =================================================
    # FD NODES
    # =================================================

    if not file_handles:

        data["fd"].x = torch.empty(
            (0, 3),
            dtype=torch.float
        )

    else:

        fd_features = []

        for file_handle in file_handles:

            is_read = (
                1.0
                if "r" in file_handle.mode
                else 0.0
            )

            is_write = (
                1.0
                if "w" in file_handle.mode
                else 0.0
            )

            is_append = (
                1.0
                if "a" in file_handle.mode
                else 0.0
            )

            fd_features.append([
                is_read,
                is_write,
                is_append
            ])

        data["fd"].x = torch.tensor(
            fd_features,
            dtype=torch.float
        )

    # =================================================
    # FD -> INODE
    # =================================================

    if file_handles:

        source_nodes = []
        target_nodes = []

        for fd_index, file_handle in enumerate(
            file_handles
        ):

            target_inode_index = (
                inode_id_to_index[
                    file_handle.inode_id
                ]
            )

            source_nodes.append(
                fd_index
            )

            target_nodes.append(
                target_inode_index
            )

        data[
            "fd",
            "open_by",
            "inode"
        ].edge_index = torch.tensor(
            [source_nodes, target_nodes],
            dtype=torch.long
        )

        # =============================================
        # INODE -> FD
        # =============================================

        data[
            "inode",
            "opened_by",
            "fd"
        ].edge_index = torch.tensor(
            [target_nodes, source_nodes],
            dtype=torch.long
        )

    # =================================================
    # RENAMES
    # =================================================

    if rename_history:

        rename_sources = []
        rename_targets = []

        for rename in rename_history:

            inode_id = rename["inode_id"]

            if inode_id in inode_id_to_index:

                inode_index = (
                    inode_id_to_index[
                        inode_id
                    ]
                )

                rename_sources.append(
                    inode_index
                )

                rename_targets.append(
                    inode_index
                )

        if rename_sources:

            data[
                "inode",
                "renames",
                "inode"
            ].edge_index = torch.tensor(
                [rename_sources, rename_targets],
                dtype=torch.long
            )

    return data
