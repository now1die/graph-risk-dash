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
    vfs.create("/home", "directory")

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
    subgraph_touched_indices = get_subgraph_touched_inode_indices(
        graph,
        touched_indices
    )

    return {
        "graph": subgraph,
        "touched_inodes": subgraph_touched_indices,
        "label": 0
    }


def create_risky_sample():

    vfs = VirtualFileSystem()

    # Create a directory
    vfs.create("/home", "directory")

    # Create several files
    vfs.create("/home/file1.txt", "file")
    vfs.create("/home/file2.txt", "file")
    vfs.create("/home/file3.txt", "file")

    # Delete one file
    transaction = vfs.unlink(
        "/home/file1.txt"
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
    subgraph_touched_indices = get_subgraph_touched_inode_indices(
        graph,
        touched_indices
    )

    return {
        "graph": subgraph,
        "touched_inodes": subgraph_touched_indices,
        "label": 1
    }


if __name__ == "__main__":

    normal_sample = create_normal_sample()

    risky_sample = create_risky_sample()

    print("NORMAL SAMPLE")
    print("Label:", normal_sample["label"])
    print("Touched:", normal_sample["touched_inodes"])
    print(normal_sample["graph"])

    print()

    print("RISKY SAMPLE")
    print("Label:", risky_sample["label"])
    print("Touched:", risky_sample["touched_inodes"])
    print(risky_sample["graph"])

    print()

    print("DATASET TEST COMPLETE")
