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
    Find inode nodes that are directly connected
    to the touched inode nodes.

    Returns the touched nodes plus their neighbors.
    """

    neighbors = set(touched_indices)

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
                neighbors.add(target)

            if target in touched_indices:
                neighbors.add(source)

    return sorted(neighbors)
