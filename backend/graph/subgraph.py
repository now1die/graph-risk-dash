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

    Returns a list of:
        (node_type, node_index)
    """

    neighbors = []

    # -------------------------------------------------
    # INODE -> DIRENT
    # -------------------------------------------------
    if node_type == "inode":

        relation = ("inode", "contains", "dirent")

        if relation in graph.edge_types:
            edge_index = graph[relation].edge_index

            for source, target in edge_index.t():
                source = int(source)
                target = int(target)

                if source == node_index:
                    neighbors.append(
                        ("dirent", target)
                    )

    # -------------------------------------------------
    # DIRENT -> INODE
    # -------------------------------------------------
    if node_type == "dirent":

        relation = ("dirent", "contains", "inode")

        if relation in graph.edge_types:
            edge_index = graph[relation].edge_index

            for source, target in edge_index.t():
                source = int(source)
                target = int(target)

                if source == node_index:
                    neighbors.append(
                        ("inode", target)
                    )

    # -------------------------------------------------
    # FD -> INODE
    # -------------------------------------------------
    if node_type == "fd":

        relation = ("fd", "open_by", "inode")

        if relation in graph.edge_types:
            edge_index = graph[relation].edge_index

            for source, target in edge_index.t():
                source = int(source)
                target = int(target)

                if source == node_index:
                    neighbors.append(
                        ("inode", target)
                    )

    # -------------------------------------------------
    # INODE -> FD
    # -------------------------------------------------
    if node_type == "inode":

        relation = ("fd", "open_by", "inode")

        if relation in graph.edge_types:
            edge_index = graph[relation].edge_index

            for source, target in edge_index.t():
                source = int(source)
                target = int(target)

                if target == node_index:
                    neighbors.append(
                        ("fd", source)
                    )

    # -------------------------------------------------
    # INODE <-> INODE LINKS
    # -------------------------------------------------
    if node_type == "inode":

        relation = ("inode", "links", "inode")

        if relation in graph.edge_types:
            edge_index = graph[relation].edge_index

            for source, target in edge_index.t():
                source = int(source)
                target = int(target)

                if source == node_index:
                    neighbors.append(
                        ("inode", target)
                    )

                if target == node_index:
                    neighbors.append(
                        ("inode", source)
                    )

    # -------------------------------------------------
    # INODE <-> INODE RENAMES
    # -------------------------------------------------
    if node_type == "inode":

        relation = ("inode", "renames", "inode")

        if relation in graph.edge_types:
            edge_index = graph[relation].edge_index

            for source, target in edge_index.t():
                source = int(source)
                target = int(target)

                if source == node_index:
                    neighbors.append(
                        ("inode", target)
                    )

                if target == node_index:
                    neighbors.append(
                        ("inode", source)
                    )

    return neighbors


def get_1hop_inode_neighbors(graph, touched_indices):
    """
    Find all nodes directly connected to
    the touched inode nodes.
    """

    result = {
        "inode": set(touched_indices),
        "dirent": set(),
        "fd": set()
    }

    for inode_index in touched_indices:

        neighbors = get_neighbors(
            graph,
            "inode",
            inode_index
        )

        for node_type, node_index in neighbors:
            result[node_type].add(node_index)

    result["inode"] = sorted(result["inode"])
    result["dirent"] = sorted(result["dirent"])
    result["fd"] = sorted(result["fd"])

    return result


def get_2hop_subgraph(graph, touched_indices):
    """
    Find all nodes within two graph hops
    of the touched inode nodes.

    Traversal works across all node types.
    """

    # -------------------------------------------------
    # STARTING NODES
    # -------------------------------------------------

    visited = set()

    frontier = []

    for inode_index in touched_indices:

        node = ("inode", inode_index)

        visited.add(node)
        frontier.append(node)

    # -------------------------------------------------
    # HOP 1 + HOP 2
    # -------------------------------------------------

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

                    visited.add(neighbor)
                    next_frontier.append(neighbor)

        frontier = next_frontier

    # -------------------------------------------------
    # CONVERT TO GROUPED RESULT
    # -------------------------------------------------

    result = {
        "inode": set(),
        "dirent": set(),
        "fd": set()
    }

    for node_type, node_index in visited:

        result[node_type].add(node_index)

    result["inode"] = sorted(result["inode"])
    result["dirent"] = sorted(result["dirent"])
    result["fd"] = sorted(result["fd"])

    return result
