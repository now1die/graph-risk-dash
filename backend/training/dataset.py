from vfs.filesystem import VirtualFileSystem

from graph.builder import build_graph

from graph.subgraph import (
    get_touched_inode_indices,
    extract_2hop_subgraph,
    get_subgraph_touched_inode_indices
)


def make_sample(vfs, transaction, label):
    """
    Convert one filesystem transaction into
    a graph training sample.
    """

    graph = build_graph(vfs)

    touched_indices = get_touched_inode_indices(
        vfs,
        transaction
    )

    subgraph = extract_2hop_subgraph(
        graph,
        touched_indices
    )

    subgraph_touched_indices = (
        get_subgraph_touched_inode_indices(
            graph,
            touched_indices
        )
    )

    return {
        "graph": subgraph,
        "touched_inodes": subgraph_touched_indices,
        "label": label
    }


# =====================================================
# NORMAL SCENARIOS
# =====================================================

def normal_create():
    vfs = VirtualFileSystem()

    vfs.create(
        "/home",
        "directory"
    )

    transaction = vfs.create(
        "/home/file.txt",
        "file"
    )

    return make_sample(
        vfs,
        transaction,
        0
    )


def normal_write():
    vfs = VirtualFileSystem()

    vfs.create(
        "/home",
        "directory"
    )

    vfs.create(
        "/home/file.txt",
        "file"
    )

    transaction = vfs.write(
        "/home/file.txt",
        100
    )

    return make_sample(
        vfs,
        transaction,
        0
    )


def normal_open_close():
    vfs = VirtualFileSystem()

    vfs.create(
        "/home",
        "directory"
    )

    vfs.create(
        "/home/file.txt",
        "file"
    )

    vfs.open(
        "/home/file.txt",
        "r"
    )

    transaction = vfs.close(3)

    return make_sample(
        vfs,
        transaction,
        0
    )


def normal_rename():
    vfs = VirtualFileSystem()

    vfs.create(
        "/home",
        "directory"
    )

    vfs.create(
        "/home/file.txt",
        "file"
    )

    transaction = vfs.rename(
        "/home/file.txt",
        "/home/document.txt"
    )

    return make_sample(
        vfs,
        transaction,
        0
    )


def normal_hard_link():
    vfs = VirtualFileSystem()

    vfs.create(
        "/home",
        "directory"
    )

    vfs.create(
        "/home/file.txt",
        "file"
    )

    transaction = vfs.link(
        "/home/file.txt",
        "/home/file_link.txt"
    )

    return make_sample(
        vfs,
        transaction,
        0
    )


# =====================================================
# RISKY SCENARIOS
# =====================================================

def risky_rename_chain():
    vfs = VirtualFileSystem()

    vfs.create(
        "/home",
        "directory"
    )

    vfs.create(
        "/home/file.txt",
        "file"
    )

    vfs.rename(
        "/home/file.txt",
        "/home/tmp1.txt"
    )

    vfs.rename(
        "/home/tmp1.txt",
        "/home/tmp2.txt"
    )

    transaction = vfs.rename(
        "/home/tmp2.txt",
        "/home/tmp3.txt"
    )

    return make_sample(
        vfs,
        transaction,
        1
    )


def risky_many_links():
    vfs = VirtualFileSystem()

    vfs.create(
        "/home",
        "directory"
    )

    vfs.create(
        "/home/file.txt",
        "file"
    )

    vfs.link(
        "/home/file.txt",
        "/home/link1.txt"
    )

    vfs.link(
        "/home/file.txt",
        "/home/link2.txt"
    )

    transaction = vfs.link(
        "/home/file.txt",
        "/home/link3.txt"
    )

    return make_sample(
        vfs,
        transaction,
        1
    )


def risky_open_write():
    vfs = VirtualFileSystem()

    vfs.create(
        "/home",
        "directory"
    )

    vfs.create(
        "/home/file.txt",
        "file"
    )

    vfs.open(
        "/home/file.txt",
        "w"
    )

    transaction = vfs.write(
        "/home/file.txt",
        1000
    )

    return make_sample(
        vfs,
        transaction,
        1
    )


def risky_mixed_operations():
    vfs = VirtualFileSystem()

    vfs.create(
        "/home",
        "directory"
    )

    vfs.create(
        "/home/file.txt",
        "file"
    )

    vfs.link(
        "/home/file.txt",
        "/home/link.txt"
    )

    vfs.rename(
        "/home/file.txt",
        "/home/tmp.txt"
    )

    transaction = vfs.rename(
        "/home/tmp.txt",
        "/home/final.txt"
    )

    return make_sample(
        vfs,
        transaction,
        1
    )


def risky_multiple_renames():
    vfs = VirtualFileSystem()

    vfs.create(
        "/home",
        "directory"
    )

    vfs.create(
        "/home/a.txt",
        "file"
    )

    vfs.create(
        "/home/b.txt",
        "file"
    )

    vfs.rename(
        "/home/a.txt",
        "/home/a1.txt"
    )

    vfs.rename(
        "/home/a1.txt",
        "/home/a2.txt"
    )

    transaction = vfs.rename(
        "/home/a2.txt",
        "/home/a3.txt"
    )

    return make_sample(
        vfs,
        transaction,
        1
    )


# =====================================================
# BUILD DATASET
# =====================================================

def generate_dataset():

    samples = []

    # Normal samples
    samples.append(normal_create())
    samples.append(normal_write())
    samples.append(normal_open_close())
    samples.append(normal_rename())
    samples.append(normal_hard_link())

    # Repeat normal scenarios with different
    # filesystem states
    samples.append(normal_create())
    samples.append(normal_write())
    samples.append(normal_open_close())
    samples.append(normal_rename())
    samples.append(normal_hard_link())

    # Risky samples
    samples.append(risky_rename_chain())
    samples.append(risky_many_links())
    samples.append(risky_open_write())
    samples.append(risky_mixed_operations())
    samples.append(risky_multiple_renames())

    # Repeat risky scenarios
    samples.append(risky_rename_chain())
    samples.append(risky_many_links())
    samples.append(risky_open_write())
    samples.append(risky_mixed_operations())
    samples.append(risky_multiple_renames())

    return samples


# =====================================================
# TEST DATASET
# =====================================================

if __name__ == "__main__":

    dataset = generate_dataset()

    print()
    print("DATASET CREATED")
    print("----------------")

    print("Total samples:", len(dataset))

    normal_count = 0
    risky_count = 0

    for index, sample in enumerate(dataset):

        if sample["label"] == 0:
            normal_count += 1
        else:
            risky_count += 1

        print(
            "Sample",
            index + 1,
            "| Label:",
            sample["label"],
            "| Touched:",
            sample["touched_inodes"],
            "| Inodes:",
            sample["graph"]["inode"].x.shape[0],
            "| Dirents:",
            sample["graph"]["dirent"].x.shape[0],
            "| Links:",
            sample["graph"]["link"].x.shape[0],
            "| FDs:",
            sample["graph"]["fd"].x.shape[0],
            "| Renames:",
            sample["graph"]["rename"].x.shape[0]
        )

    print()
    print("NORMAL SAMPLES:", normal_count)
    print("RISKY SAMPLES:", risky_count)

    print()
    print("DATASET TEST COMPLETE")
