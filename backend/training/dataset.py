from vfs.filesystem import VirtualFileSystem

from graph.builder import build_graph

from graph.subgraph import (
    get_touched_inode_indices,
    extract_2hop_subgraph,
    get_subgraph_touched_inode_indices
)


def create_normal_sample():

    vfs = VirtualFileSystem()

    # Create a normal directory
    vfs.create(
        "/home",
        "directory"
    )

    # Create a normal file
    transaction = vfs.create(
        "/home/test.txt",
        "file"
    )

    # Build graph from current filesystem
    graph = build_graph(vfs)

    # Find inode indices touched by the transaction
    touched_indices = get_touched_inode_indices(
        vfs,
        transaction
    )

    # Extract the 2-hop neighborhood
    subgraph = extract_2hop_subgraph(
        graph,
        touched_indices
    )

    # Convert touched inode indices
    # from full graph to subgraph indices
    subgraph_touched_indices = (
        get_subgraph_touched_inode_indices(
            graph,
            touched_indices
        )
    )

    return {
        "graph": subgraph,
        "touched_inodes": subgraph_touched_indices,
        "label": 0
    }


def create_risky_sample():

    vfs = VirtualFileSystem()

    # Create a directory
    vfs.create(
        "/home",
        "directory"
    )

    # Create a file
    vfs.create(
        "/home/file.txt",
        "file"
    )

    # Perform a sequence of renames
    vfs.rename(
        "/home/file.txt",
        "/home/tmp1.txt"
    )

    vfs.rename(
        "/home/tmp1.txt",
        "/home/tmp2.txt"
    )

    # Final rename transaction
    transaction = vfs.rename(
        "/home/tmp2.txt",
        "/home/tmp3.txt"
    )

    # Build graph from current filesystem
    graph = build_graph(vfs)

    # Find inode indices touched by the transaction
    touched_indices = get_touched_inode_indices(
        vfs,
        transaction
    )

    # Extract the 2-hop neighborhood
    subgraph = extract_2hop_subgraph(
        graph,
        touched_indices
    )

    # Convert touched inode indices
    # from full graph to subgraph indices
    subgraph_touched_indices = (
        get_subgraph_touched_inode_indices(
            graph,
            touched_indices
        )
    )

    return {
        "graph": subgraph,
        "touched_inodes": subgraph_touched_indices,
        "label": 1
    }


if __name__ == "__main__":

    # =============================================
    # CREATE NORMAL SAMPLE
    # =============================================

    normal_sample = create_normal_sample()

    print("NORMAL SAMPLE")
    print("Label:", normal_sample["label"])
    print("Touched:", normal_sample["touched_inodes"])
    print(normal_sample["graph"])

    print()

    # =============================================
    # CREATE RISKY SAMPLE
    # =============================================

    risky_sample = create_risky_sample()

    print("RISKY SAMPLE")
    print("Label:", risky_sample["label"])
    print("Touched:", risky_sample["touched_inodes"])
    print(risky_sample["graph"])

    print()

    # =============================================
    # COMPLETE
    # =============================================

    print("DATASET TEST COMPLETE")
