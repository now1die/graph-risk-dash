def get_touched_inode_indices(vfs, transaction):
    """
    Convert transaction inode IDs into
    zero-based graph node indices.
    """

    inodes = vfs.get_all_inodes()

    inode_id_to_index = {
        inode.inode_id: index
        for index, inode in enumerate(inodes)
    }

    touched_indices = []

    for inode_id in transaction.inodes_touched:

        if inode_id in inode_id_to_index:
            touched_indices.append(
                inode_id_to_index[inode_id]
            )

    return touched_indices


def get_neighbors(graph, node_type, node_index):
    """
    Find all nodes directly connected to one node.

    Returns:
        (node_type, node_index)
    """

    neighbors = []

    # =================================================
    # INODE -> DIRENT
    # =================================================

    if node_type == "inode":

        relation = (
            "inode",
            "contains",
            "dirent"
        )

        if relation in graph.edge_types:

            for source, target in (
                graph[relation].edge_index.t()
            ):

                source = int(source)
                target = int(target)

                if source == node_index:
                    neighbors.append(
                        ("dirent", target)
                    )

    # =================================================
    # DIRENT -> INODE
    # =================================================

    if node_type == "dirent":

        relation = (
            "dirent",
            "points_to",
            "inode"
        )

        if relation in graph.edge_types:

            for source, target in (
                graph[relation].edge_index.t()
            ):

                source = int(source)
                target = int(target)

                if source == node_index:
                    neighbors.append(
                        ("inode", target)
                    )

    # =================================================
    # INODE -> LINK
    # =================================================

    if node_type == "inode":

        relation = (
            "inode",
            "has_link",
            "link"
        )

        if relation in graph.edge_types:

            for source, target in (
                graph[relation].edge_index.t()
            ):

                source = int(source)
                target = int(target)

                if source == node_index:
                    neighbors.append(
                        ("link", target)
                    )

    # =================================================
    # LINK -> INODE
    # =================================================

    if node_type == "link":

        relation = (
            "link",
            "points_to",
            "inode"
        )

        if relation in graph.edge_types:

            for source, target in (
                graph[relation].edge_index.t()
            ):

                source = int(source)
                target = int(target)

                if source == node_index:
                    neighbors.append(
                        ("inode", target)
                    )

    # =================================================
    # FD -> INODE
    # =================================================

    if node_type == "fd":

        relation = (
            "fd",
            "open_by",
            "inode"
        )

        if relation in graph.edge_types:

            for source, target in (
                graph[relation].edge_index.t()
            ):

                source = int(source)
                target = int(target)

                if source == node_index:
                    neighbors.append(
                        ("inode", target)
                    )

    # =================================================
    # INODE -> FD
    # =================================================

    if node_type == "inode":

        relation = (
            "inode",
            "opened_by",
            "fd"
        )

        if relation in graph.edge_types:

            for source, target in (
                graph[relation].edge_index.t()
            ):

                source = int(source)
                target = int(target)

                if source == node_index:
                    neighbors.append(
                        ("fd", target)
                    )

    # =================================================
    # INODE -> RENAME
    # =================================================

    if node_type == "inode":

        relation = (
            "inode",
            "rename_source",
            "rename"
        )

        if relation in graph.edge_types:

            for source, target in (
                graph[relation].edge_index.t()
            ):

                source = int(source)
                target = int(target)

                if source == node_index:
                    neighbors.append(
                        ("rename", target)
                    )

    # =================================================
    # RENAME -> INODE
    # =================================================

    if node_type == "rename":

        relation = (
            "rename",
            "rename_target",
            "inode"
        )

        if relation in graph.edge_types:

            for source, target in (
                graph[relation].edge_index.t()
            ):

                source = int(source)
                target = int(target)

                if source == node_index:
                    neighbors.append(
                        ("inode", target)
                    )

    return neighbors


def get_1hop_inode_neighbors(
    graph,
    touched_indices
):
    """
    Find all nodes directly connected
    to the touched inode nodes.
    """

    result = {
        "inode": set(touched_indices),
        "dirent": set(),
        "fd": set(),
        "link": set(),
        "rename": set()
    }

    for inode_index in touched_indices:

        neighbors = get_neighbors(
            graph,
            "inode",
            inode_index
        )

        for node_type, node_index in neighbors:

            result[node_type].add(
                node_index
            )

    for node_type in result:

        result[node_type] = sorted(
            result[node_type]
        )

    return result


def get_2hop_subgraph(
    graph,
    touched_indices
):
    """
    Find all nodes within two graph hops
    of the touched inode nodes.
    """

    visited = set()
    frontier = []

    # =================================================
    # START
    # =================================================

    for inode_index in touched_indices:

        node = (
            "inode",
            inode_index
        )

        visited.add(node)
        frontier.append(node)

    # =================================================
    # TWO HOPS
    # =================================================

    for _ in range(2):

        next_frontier = []

        for node_type, node_index in frontier:

            neighbors = get_neighbors(
                graph,
                node_type,
                node_index
            )

            for neighbor in neighbors:

                if neighbor not in visited:

                    visited.add(
                        neighbor
                    )

                    next_frontier.append(
                        neighbor
                    )

        frontier = next_frontier

    # =================================================
    # GROUP RESULTS
    # =================================================

    result = {
        "inode": set(),
        "dirent": set(),
        "fd": set(),
        "link": set(),
        "rename": set()
    }

    for node_type, node_index in visited:

        result[node_type].add(
            node_index
        )

    for node_type in result:

        result[node_type] = sorted(
            result[node_type]
        )

    return result
