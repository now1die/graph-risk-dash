from vfs.filesystem import VirtualFileSystem

from graph.builder import build_graph

from graph.subgraph import (
    get_touched_inode_indices,
    extract_2hop_subgraph,
    get_subgraph_touched_inode_indices
)

import random


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

def normal_create(file_number):
    vfs = VirtualFileSystem()

    vfs.create("/home", "directory")

    for i in range(1, file_number):
        vfs.create(
            "/home/file" + str(i) + ".txt",
            "file"
        )

    transaction = vfs.create(
        "/home/file" + str(file_number) + ".txt",
        "file"
    )

    return make_sample(vfs, transaction, 0)


def normal_write(size):
    vfs = VirtualFileSystem()

    vfs.create("/home", "directory")

    vfs.create(
        "/home/file.txt",
        "file"
    )

    transaction = vfs.write(
        "/home/file.txt",
        size
    )

    return make_sample(vfs, transaction, 0)


def normal_open_close(mode):
    vfs = VirtualFileSystem()

    vfs.create("/home", "directory")

    vfs.create(
        "/home/file.txt",
        "file"
    )

    vfs.open(
        "/home/file.txt",
        mode
    )

    transaction = vfs.close(3)

    return make_sample(vfs, transaction, 0)


def normal_rename(number_of_files):
    vfs = VirtualFileSystem()

    vfs.create("/home", "directory")

    for i in range(1, number_of_files + 1):
        vfs.create(
            "/home/file" + str(i) + ".txt",
            "file"
        )

    transaction = vfs.rename(
        "/home/file1.txt",
        "/home/document.txt"
    )

    return make_sample(vfs, transaction, 0)


def normal_hard_link(number_of_existing_files):
    vfs = VirtualFileSystem()

    vfs.create("/home", "directory")

    for i in range(1, number_of_existing_files + 1):
        vfs.create(
            "/home/file" + str(i) + ".txt",
            "file"
        )

    transaction = vfs.link(
        "/home/file1.txt",
        "/home/file1_link.txt"
    )

    return make_sample(vfs, transaction, 0)


# =====================================================
# RISKY SCENARIOS
# =====================================================

def risky_rename_chain(number_of_renames):
    vfs = VirtualFileSystem()

    vfs.create("/home", "directory")

    vfs.create(
        "/home/file.txt",
        "file"
    )

    current_path = "/home/file.txt"

    for i in range(1, number_of_renames + 1):

        new_path = (
            "/home/tmp"
            + str(i)
            + ".txt"
        )

        transaction = vfs.rename(
            current_path,
            new_path
        )

        current_path = new_path

    return make_sample(vfs, transaction, 1)


def risky_many_links(number_of_links):
    vfs = VirtualFileSystem()

    vfs.create("/home", "directory")

    vfs.create(
        "/home/file.txt",
        "file"
    )

    for i in range(1, number_of_links):

        vfs.link(
            "/home/file.txt",
            "/home/link"
            + str(i)
            + ".txt"
        )

    transaction = vfs.link(
        "/home/file.txt",
        "/home/link"
        + str(number_of_links)
        + ".txt"
    )

    return make_sample(vfs, transaction, 1)


def risky_mixed_operations(
    number_of_renames,
    number_of_links
):
    vfs = VirtualFileSystem()

    vfs.create("/home", "directory")

    vfs.create(
        "/home/file.txt",
        "file"
    )

    for i in range(1, number_of_links + 1):

        vfs.link(
            "/home/file.txt",
            "/home/link"
            + str(i)
            + ".txt"
        )

    current_path = "/home/file.txt"

    for i in range(1, number_of_renames + 1):

        new_path = (
            "/home/tmp"
            + str(i)
            + ".txt"
        )

        transaction = vfs.rename(
            current_path,
            new_path
        )

        current_path = new_path

    return make_sample(vfs, transaction, 1)


def risky_multiple_file_renames(number_of_files):
    vfs = VirtualFileSystem()

    vfs.create("/home", "directory")

    for i in range(1, number_of_files + 1):

        vfs.create(
            "/home/file"
            + str(i)
            + ".txt",
            "file"
        )

    for i in range(1, number_of_files):

        vfs.rename(
            "/home/file"
            + str(i) + ".txt",
            "/home/tmp"
            + str(i) + ".txt"
        )

    transaction = vfs.rename(
        "/home/file"
        + str(number_of_files)
        + ".txt",
        "/home/tmp"
        + str(number_of_files)
        + ".txt"
    )

    return make_sample(vfs, transaction, 1)


# =====================================================
# BUILD DATASET
# =====================================================

def generate_dataset():

    samples = []

    # -------------------------------------------------
    # NORMAL SAMPLES
    # -------------------------------------------------

    samples.append(normal_create(1))
    samples.append(normal_create(2))
    samples.append(normal_create(3))
    samples.append(normal_create(4))

    samples.append(normal_write(10))
    samples.append(normal_write(100))
    samples.append(normal_write(500))
    samples.append(normal_write(1000))

    samples.append(normal_open_close("r"))
    samples.append(normal_open_close("w"))
    samples.append(normal_open_close("a"))

    samples.append(normal_rename(1))
    samples.append(normal_rename(2))
    samples.append(normal_rename(3))

    samples.append(normal_hard_link(1))
    samples.append(normal_hard_link(2))
    samples.append(normal_hard_link(3))

    samples.append(normal_create(5))
    samples.append(normal_write(250))
    samples.append(normal_write(750))

    # -------------------------------------------------
    # RISKY SAMPLES
    # -------------------------------------------------

    samples.append(risky_rename_chain(2))
    samples.append(risky_rename_chain(3))
    samples.append(risky_rename_chain(4))
    samples.append(risky_rename_chain(5))

    samples.append(risky_many_links(2))
    samples.append(risky_many_links(3))
    samples.append(risky_many_links(4))
    samples.append(risky_many_links(5))

    samples.append(risky_mixed_operations(2, 2))
    samples.append(risky_mixed_operations(3, 2))
    samples.append(risky_mixed_operations(2, 3))
    samples.append(risky_mixed_operations(3, 3))
    samples.append(risky_mixed_operations(4, 3))

    samples.append(risky_multiple_file_renames(2))
    samples.append(risky_multiple_file_renames(3))
    samples.append(risky_multiple_file_renames(4))

    samples.append(risky_rename_chain(6))
    samples.append(risky_many_links(6))
    samples.append(risky_mixed_operations(4, 4))
    samples.append(risky_multiple_file_renames(5))

    return samples


# =====================================================
# SPLIT DATASET
# =====================================================

def split_dataset(samples):

    normal_samples = []
    risky_samples = []

    for sample in samples:

        if sample["label"] == 0:
            normal_samples.append(sample)

        else:
            risky_samples.append(sample)

    # Shuffle both classes separately
    random.shuffle(normal_samples)
    random.shuffle(risky_samples)

    # 70% of each class for training
    # 15% of each class for validation
    # 15% of each class for testing

    normal_train = normal_samples[:14]
    normal_validation = normal_samples[14:17]
    normal_test = normal_samples[17:20]

    risky_train = risky_samples[:14]
    risky_validation = risky_samples[14:17]
    risky_test = risky_samples[17:20]

    train_samples = normal_train + risky_train
    validation_samples = (
        normal_validation +
        risky_validation
    )
    test_samples = normal_test + risky_test

    # Shuffle final splits
    random.shuffle(train_samples)
    random.shuffle(validation_samples)
    random.shuffle(test_samples)

    return (
        train_samples,
        validation_samples,
        test_samples
    )


# =====================================================
# TEST DATASET
# =====================================================

if __name__ == "__main__":

    dataset = generate_dataset()

    train_samples, validation_samples, test_samples = (
        split_dataset(dataset)
    )

    print()
    print("DATASET CREATED")
    print("----------------")

    print(
        "Total samples:",
        len(dataset)
    )

    print()
    print("TRAINING SET")
    print("------------")

    train_normal = sum(
        1 for sample in train_samples
        if sample["label"] == 0
    )

    train_risky = sum(
        1 for sample in train_samples
        if sample["label"] == 1
    )

    print(
        "Total:",
        len(train_samples)
    )

    print(
        "Normal:",
        train_normal
    )

    print(
        "Risky:",
        train_risky
    )

    print()
    print("VALIDATION SET")
    print("--------------")

    validation_normal = sum(
        1 for sample in validation_samples
        if sample["label"] == 0
    )

    validation_risky = sum(
        1 for sample in validation_samples
        if sample["label"] == 1
    )

    print(
        "Total:",
        len(validation_samples)
    )

    print(
        "Normal:",
        validation_normal
    )

    print(
        "Risky:",
        validation_risky
    )

    print()
    print("TEST SET")
    print("--------")

    test_normal = sum(
        1 for sample in test_samples
        if sample["label"] == 0
    )

    test_risky = sum(
        1 for sample in test_samples
        if sample["label"] == 1
    )

    print(
        "Total:",
        len(test_samples)
    )

    print(
        "Normal:",
        test_normal
    )

    print(
        "Risky:",
        test_risky
    )

    print()
    print("DATASET SPLIT TEST COMPLETE")
