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
    - link
    - rename

    Relations:
    - inode -> dirent : contains
    - dirent -> inode : points_to

    - inode -> link   : has_link
    - link -> inode   : points_to

    - fd -> inode     : open_by
    - inode -> fd     : opened_by

    - inode -> rename : rename_source
    - rename -> inode : rename_target
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
    # LINK NODES
    # =================================================

    link_nodes = []

    for inode_id, inode_dirents in {}.items():
        pass

    paths_by_inode = {}

    for dirent in dirents:

        inode_id = dirent.inode_id

        if inode_id not in paths_by_inode:
            paths_by_inode[inode_id] = []

        paths_by_inode[inode_id].append(
            dirent
        )

    link_source_nodes = []
    link_target_nodes = []

    link_index = 0

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

                link_nodes.append(
                    [1.0]
                )

                link_source_nodes.append(
                    inode_index
                )

                link_target_nodes.append(
                    link_index
                )

                link_index += 1

    if link_nodes:

        data["link"].x = torch.tensor(
            link_nodes,
            dtype=torch.float
        )

        data[
            "inode",
            "has_link",
            "link"
        ].edge_index = torch.tensor(
            [
                link_source_nodes,
                link_target_nodes
            ],
            dtype=torch.long
        )

        data[
            "link",
            "points_to",
            "inode"
        ].edge_index = torch.tensor(
            [
                link_target_nodes,
                link_source_nodes
            ],
            dtype=torch.long
        )

    else:

        data["link"].x = torch.empty(
            (0, 1),
            dtype=torch.float
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

        data[
            "inode",
            "opened_by",
            "fd"
        ].edge_index = torch.tensor(
            [target_nodes, source_nodes],
            dtype=torch.long
        )

    # =================================================
    # RENAME NODES
    # =================================================

    rename_features = []

    rename_source_nodes = []
    rename_target_nodes = []

    for rename_index, rename in enumerate(
        rename_history
    ):

        inode_id = rename["inode_id"]

        if inode_id not in inode_id_to_index:
            continue

        old_path = rename["old_path"]
        new_path = rename["new_path"]

        old_path_length = len(
            old_path
        )

        new_path_length = len(
            new_path
        )

        rename_features.append([
            float(old_path_length),
            float(new_path_length)
        ])

        inode_index = (
            inode_id_to_index[inode_id]
        )

        rename_source_nodes.append(
            inode_index
        )

        rename_target_nodes.append(
            rename_index
        )

    if rename_features:

        data["rename"].x = torch.tensor(
            rename_features,
            dtype=torch.float
        )

        data[
            "inode",
            "rename_source",
            "rename"
        ].edge_index = torch.tensor(
            [
                rename_source_nodes,
                rename_target_nodes
            ],
            dtype=torch.long
        )

        data[
            "rename",
            "rename_target",
            "inode"
        ].edge_index = torch.tensor(
            [
                rename_target_nodes,
                rename_source_nodes
            ],
            dtype=torch.long
        )

    else:

        data["rename"].x = torch.empty(
            (0, 2),
            dtype=torch.float
        )

    return data
