import torch
from torch_geometric.data import HeteroData


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


def extract_2hop_subgraph(
    graph,
    touched_indices
):
    """
    Extract the actual 2-hop HeteroData graph.

    This uses get_2hop_subgraph() to determine which
    nodes belong to the neighborhood and then copies
    their features and relevant edges into a new graph.

    Returns:
        HeteroData containing only the 2-hop neighborhood.
    """

    node_indices = get_2hop_subgraph(
        graph,
        touched_indices
    )

    subgraph = HeteroData()

    node_types = [
        "inode",
        "dirent",
        "fd",
        "link",
        "rename"
    ]

    # =================================================
    # COPY NODE FEATURES
    # =================================================

    for node_type in node_types:

        indices = node_indices[node_type]

        if len(indices) == 0:

            feature_size = graph[node_type].x.size(1)

            subgraph[node_type].x = torch.empty(
                (0, feature_size),
                dtype=graph[node_type].x.dtype
            )

        else:

            index_tensor = torch.tensor(
                indices,
                dtype=torch.long
            )

            subgraph[node_type].x = (
                graph[node_type].x[
                    index_tensor
                ]
            )

    # =================================================
    # CREATE OLD -> NEW INDEX MAPS
    # =================================================

    index_maps = {}

    for node_type in node_types:

        index_maps[node_type] = {
            old_index: new_index
            for new_index, old_index
            in enumerate(node_indices[node_type])
        }

    # =================================================
    # COPY EDGES
    # =================================================

    for edge_type in graph.edge_types:

        source_type, relation, target_type = edge_type

        if (
            source_type not in index_maps
            or target_type not in index_maps
        ):
            continue

        old_edges = graph[edge_type].edge_index

        new_edges = []

        for source, target in old_edges.t():

            source = int(source)
            target = int(target)

            if (
                source in index_maps[source_type]
                and target in index_maps[target_type]
            ):

                new_source = index_maps[source_type][source]
                new_target = index_maps[target_type][target]

                new_edges.append(
                    [new_source, new_target]
                )

        if len(new_edges) == 0:

            subgraph[edge_type].edge_index = torch.empty(
                (2, 0),
                dtype=torch.long
            )

        else:

            subgraph[edge_type].edge_index = torch.tensor(
                new_edges,
                dtype=torch.long
            ).t().contiguous()

    return subgraph
def get_subgraph_touched_inode_indices(
    graph,
    touched_indices
):
    """
    Convert original touched inode indices into
    their new indices inside the extracted 2-hop subgraph.
    """

    node_indices = get_2hop_subgraph(
        graph,
        touched_indices
    )

    index_map = {
        old_index: new_index
        for new_index, old_index
        in enumerate(node_indices["inode"])
    }

    new_touched_indices = []

    for old_index in touched_indices:

        if old_index in index_map:

            new_touched_indices.append(
                index_map[old_index]
            )

    return new_touched_indices    
