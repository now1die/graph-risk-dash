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


def get_1hop_inode_neighbors(graph, touched_indices):
    """
    Find nodes directly connected to the touched inode nodes.

    Returns node identifiers grouped by node type.
    """

    result = {
        "inode": set(touched_indices),
        "dirent": set(),
        "fd": set()
    }

    # ---------------------------------------------------------
    # CONTAINS
    # dirent -> inode
    # ---------------------------------------------------------

    relation = ("dirent", "contains", "inode")

    if relation in graph.edge_types:

        edge_index = graph[relation].edge_index

        for source, target in edge_index.t():

            source = int(source)
            target = int(target)

            if target in touched_indices:
                result["dirent"].add(source)

    # ---------------------------------------------------------
    # OPEN_BY
    # fd -> inode
    # ---------------------------------------------------------

    relation = ("fd", "open_by", "inode")

    if relation in graph.edge_types:

        edge_index = graph[relation].edge_index

        for source, target in edge_index.t():

            source = int(source)
            target = int(target)

            if target in touched_indices:
                result["fd"].add(source)

    # ---------------------------------------------------------
    # INODE -> INODE RELATIONS
    # ---------------------------------------------------------

    inode_relations = [
        ("inode", "links", "inode"),
        ("inode", "renames", "inode")
    ]

    for relation in inode_relations:

        if relation not in graph.edge_types:
            continue

        edge_index = graph[relation].edge_index

        for source, target in edge_index.t():

            source = int(source)
            target = int(target)

            if source in touched_indices:
                result["inode"].add(target)

            if target in touched_indices:
                result["inode"].add(source)

    result["inode"] = sorted(result["inode"])
    result["dirent"] = sorted(result["dirent"])
    result["fd"] = sorted(result["fd"])

    return result


def get_2hop_subgraph(graph, touched_indices):
    """
    Find the nodes within two graph hops
    of the touched inode nodes.

    Returns node identifiers grouped by node type.
    """

    # Start with the touched nodes
    result = {
        "inode": set(touched_indices),
        "dirent": set(),
        "fd": set()
    }

    # First hop
    first_hop = get_1hop_inode_neighbors(
        graph,
        touched_indices
    )

    for node_type in result:
        result[node_type].update(
            first_hop[node_type]
        )

    # ---------------------------------------------------------
    # Second hop
    # ---------------------------------------------------------

    current_inodes = list(result["inode"])

    second_hop = get_1hop_inode_neighbors(
        graph,
        current_inodes
    )

    for node_type in result:
        result[node_type].update(
            second_hop[node_type]
        )

    # Convert sets to sorted lists
    result["inode"] = sorted(result["inode"])
    result["dirent"] = sorted(result["dirent"])
    result["fd"] = sorted(result["fd"])

    return result
