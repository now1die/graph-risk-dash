import torch

from vfs.filesystem import VirtualFileSystem
from graph.builder import build_graph
from graph.subgraph import get_touched_inode_indices
from gnn.model import RiskGNN


# -----------------------------------------
# CREATE TEST FILESYSTEM
# -----------------------------------------

vfs = VirtualFileSystem()

vfs.create(
    "/home",
    "directory"
)

tx = vfs.create(
    "/home/test.txt",
    "file"
)

vfs.create(
    "/home/other.txt",
    "file"
)


# -----------------------------------------
# BUILD GRAPH
# -----------------------------------------

graph = build_graph(vfs)

print("GRAPH:")
print(graph)

print()
print("EDGE TYPES:")
print(graph.edge_types)


# -----------------------------------------
# FIND TOUCHED INODES
# -----------------------------------------

touched_indices = get_touched_inode_indices(
    vfs,
    tx
)

print()
print("TOUCHED INODE INDICES:")
print(touched_indices)


# -----------------------------------------
# CREATE MODEL
# -----------------------------------------

model = RiskGNN()

model.eval()


# -----------------------------------------
# FORWARD PASS
# -----------------------------------------

with torch.no_grad():

    risk_logit = model(
        graph.x_dict,
        graph.edge_index_dict,
        touched_indices
    )

    risk_probability = torch.sigmoid(
        risk_logit
    )


# -----------------------------------------
# PRINT RESULT
# -----------------------------------------

print()
print("RISK LOGIT:")
print(risk_logit)

print()
print("RISK PROBABILITY:")
print(risk_probability)
