import torch

from vfs.filesystem import VirtualFileSystem
from graph.builder import build_graph
from graph.subgraph import (
    get_touched_inode_indices,
    get_2hop_subgraph,
    extract_2hop_subgraph,
    get_subgraph_touched_inode_indices
)
from gnn.model import RiskGNN


# =========================================
# CREATE FILESYSTEM
# =========================================

vfs = VirtualFileSystem()

vfs.create(
    "/home",
    "directory"
)

vfs.create(
    "/home/test.txt",
    "file"
)

vfs.create(
    "/home/data.txt",
    "file"
)


# =========================================
# HARD LINK
# =========================================

vfs.link(
    "/home/test.txt",
    "/home/test_link.txt"
)


# =========================================
# RENAME
# =========================================

rename_tx = vfs.rename(
    "/home/data.txt",
    "/home/renamed.txt"
)


# =========================================
# OPEN FILE
# =========================================

open_tx = vfs.open(
    "/home/test.txt",
    "r"
)


# =========================================
# BUILD GRAPH
# =========================================

graph = build_graph(vfs)

print("=========================================")
print("GRAPH")
print("=========================================")
print(graph)


print()
print("=========================================")
print("NODE TYPES")
print("=========================================")
print(graph.node_types)


print()
print("=========================================")
print("EDGE TYPES")
print("=========================================")
print(graph.edge_types)


# =========================================
# PRINT NODE FEATURES
# =========================================

print()
print("=========================================")
print("LINK FEATURES")
print("=========================================")
print(graph["link"].x)


print()
print("=========================================")
print("RENAME FEATURES")
print("=========================================")
print(graph["rename"].x)


print()
print("=========================================")
print("FD FEATURES")
print("=========================================")
print(graph["fd"].x)


# =========================================
# PRINT IMPORTANT EDGES
# =========================================

print()
print("=========================================")
print("LINK EDGES")
print("=========================================")
print(
    graph[
        "inode",
        "has_link",
        "link"
    ].edge_index
)

print(
    graph[
        "link",
        "points_to",
        "inode"
    ].edge_index
)


print()
print("=========================================")
print("RENAME EDGES")
print("=========================================")
print(
    graph[
        "inode",
        "rename_source",
        "rename"
    ].edge_index
)

print(
    graph[
        "rename",
        "rename_target",
        "inode"
    ].edge_index
)


print()
print("=========================================")
print("OPEN EDGES")
print("=========================================")
print(
    graph[
        "fd",
        "open_by",
        "inode"
    ].edge_index
)

print(
    graph[
        "inode",
        "opened_by",
        "fd"
    ].edge_index
)


# =========================================
# TOUCHED INODES
# =========================================

touched_indices = get_touched_inode_indices(
    vfs,
    rename_tx
)

print()
print("=========================================")
print("TOUCHED INODE INDICES")
print("=========================================")
print(touched_indices)


# =========================================
# 2-HOP SUBGRAPH INDICES
# =========================================

subgraph_indices = get_2hop_subgraph(
    graph,
    touched_indices
)

print()
print("=========================================")
print("2-HOP SUBGRAPH INDICES")
print("=========================================")
print(subgraph_indices)


# =========================================
# EXTRACT ACTUAL 2-HOP GRAPH
# =========================================

subgraph = extract_2hop_subgraph(
    graph,
    touched_indices
)

print()
print("=========================================")
print("EXTRACTED 2-HOP GRAPH")
print("=========================================")
print(subgraph)


# =========================================
# SUBGRAPH TOUCHED INODE INDICES
# =========================================

subgraph_touched_indices = get_subgraph_touched_inode_indices(
    graph,
    touched_indices
)

print()
print("=========================================")
print("SUBGRAPH TOUCHED INODE INDICES")
print("=========================================")
print(subgraph_touched_indices)


# =========================================
# EXTRACTED NODE TYPES
# =========================================

print()
print("=========================================")
print("EXTRACTED NODE TYPES")
print("=========================================")
print(subgraph.node_types)


# =========================================
# EXTRACTED EDGE TYPES
# =========================================

print()
print("=========================================")
print("EXTRACTED EDGE TYPES")
print("=========================================")
print(subgraph.edge_types)


# =========================================
# EXTRACTED NODE COUNTS
# =========================================

print()
print("=========================================")
print("EXTRACTED NODE COUNTS")
print("=========================================")

for node_type in subgraph.node_types:

    print(
        node_type,
        subgraph[node_type].x.shape
    )


# =========================================
# EXTRACTED EDGE COUNTS
# =========================================

print()
print("=========================================")
print("EXTRACTED EDGE COUNTS")
print("=========================================")

for edge_type in subgraph.edge_types:

    print(
        edge_type,
        subgraph[edge_type].edge_index.shape
    )


# =========================================
# CREATE GNN
# =========================================

model = RiskGNN()

model.eval()


# =========================================
# GNN FORWARD PASS
# =========================================

with torch.no_grad():

    risk_logit = model(
        subgraph.x_dict,
        subgraph.edge_index_dict,
        subgraph_touched_indices
    )

    risk_probability = torch.sigmoid(
        risk_logit
    )


# =========================================
# RESULT
# =========================================

print()
print("=========================================")
print("RISK LOGIT")
print("=========================================")
print(risk_logit)


print()
print("=========================================")
print("RISK PROBABILITY")
print("=========================================")
print(risk_probability)


print()
print("=========================================")
print("TEST COMPLETE")
print("=========================================")
