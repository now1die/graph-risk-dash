import torch
import torch.nn as nn
from torch_geometric.nn import HeteroConv, GATConv


class RiskGNN(nn.Module):

    def __init__(
        self,
        hidden_dim=32,
        heads=4,
        dropout=0.2
    ):
        super().__init__()

        # -----------------------------------------
        # INPUT ENCODERS
        # -----------------------------------------

        self.inode_encoder = nn.Sequential(
            nn.LazyLinear(hidden_dim),
            nn.ReLU()
        )

        self.dirent_encoder = nn.Sequential(
            nn.LazyLinear(hidden_dim),
            nn.ReLU()
        )

        self.fd_encoder = nn.Sequential(
            nn.LazyLinear(hidden_dim),
            nn.ReLU()
        )

        self.link_encoder = nn.Sequential(
            nn.LazyLinear(hidden_dim),
            nn.ReLU()
        )

        self.rename_encoder = nn.Sequential(
            nn.LazyLinear(hidden_dim),
            nn.ReLU()
        )

        # -----------------------------------------
        # FIRST GAT LAYER
        # -----------------------------------------

        self.conv1 = HeteroConv({

            # inode -> dirent
            ("inode", "contains", "dirent"):
                GATConv(
                    (hidden_dim, hidden_dim),
                    hidden_dim,
                    heads=heads,
                    concat=True,
                    dropout=dropout,
                    add_self_loops=False
                ),

            # dirent -> inode
            ("dirent", "points_to", "inode"):
                GATConv(
                    (hidden_dim, hidden_dim),
                    hidden_dim,
                    heads=heads,
                    concat=True,
                    dropout=dropout,
                    add_self_loops=False
                ),

            # inode -> link
            ("inode", "has_link", "link"):
                GATConv(
                    (hidden_dim, hidden_dim),
                    hidden_dim,
                    heads=heads,
                    concat=True,
                    dropout=dropout,
                    add_self_loops=False
                ),

            # link -> inode
            ("link", "points_to", "inode"):
                GATConv(
                    (hidden_dim, hidden_dim),
                    hidden_dim,
                    heads=heads,
                    concat=True,
                    dropout=dropout,
                    add_self_loops=False
                ),

            # fd -> inode
            ("fd", "open_by", "inode"):
                GATConv(
                    (hidden_dim, hidden_dim),
                    hidden_dim,
                    heads=heads,
                    concat=True,
                    dropout=dropout,
                    add_self_loops=False
                ),

            # inode -> fd
            ("inode", "opened_by", "fd"):
                GATConv(
                    (hidden_dim, hidden_dim),
                    hidden_dim,
                    heads=heads,
                    concat=True,
                    dropout=dropout,
                    add_self_loops=False
                ),

            # inode -> rename
            ("inode", "rename_source", "rename"):
                GATConv(
                    (hidden_dim, hidden_dim),
                    hidden_dim,
                    heads=heads,
                    concat=True,
                    dropout=dropout,
                    add_self_loops=False
                ),

            # rename -> inode
            ("rename", "rename_target", "inode"):
                GATConv(
                    (hidden_dim, hidden_dim),
                    hidden_dim,
                    heads=heads,
                    concat=True,
                    dropout=dropout,
                    add_self_loops=False
                )

        }, aggr="sum")

        # First layer output:
        # 32 dimensions × 4 heads = 128

        conv1_dim = hidden_dim * heads

        # -----------------------------------------
        # SECOND GAT LAYER
        # -----------------------------------------

        self.conv2 = HeteroConv({

            ("inode", "contains", "dirent"):
                GATConv(
                    (conv1_dim, conv1_dim),
                    hidden_dim,
                    heads=1,
                    concat=False,
                    dropout=dropout,
                    add_self_loops=False
                ),

            ("dirent", "points_to", "inode"):
                GATConv(
                    (conv1_dim, conv1_dim),
                    hidden_dim,
                    heads=1,
                    concat=False,
                    dropout=dropout,
                    add_self_loops=False
                ),

            ("inode", "has_link", "link"):
                GATConv(
                    (conv1_dim, conv1_dim),
                    hidden_dim,
                    heads=1,
                    concat=False,
                    dropout=dropout,
                    add_self_loops=False
                ),

            ("link", "points_to", "inode"):
                GATConv(
                    (conv1_dim, conv1_dim),
                    hidden_dim,
                    heads=1,
                    concat=False,
                    dropout=dropout,
                    add_self_loops=False
                ),

            ("fd", "open_by", "inode"):
                GATConv(
                    (conv1_dim, conv1_dim),
                    hidden_dim,
                    heads=1,
                    concat=False,
                    dropout=dropout,
                    add_self_loops=False
                ),

            ("inode", "opened_by", "fd"):
                GATConv(
                    (conv1_dim, conv1_dim),
                    hidden_dim,
                    heads=1,
                    concat=False,
                    dropout=dropout,
                    add_self_loops=False
                ),

            ("inode", "rename_source", "rename"):
                GATConv(
                    (conv1_dim, conv1_dim),
                    hidden_dim,
                    heads=1,
                    concat=False,
                    dropout=dropout,
                    add_self_loops=False
                ),

            ("rename", "rename_target", "inode"):
                GATConv(
                    (conv1_dim, conv1_dim),
                    hidden_dim,
                    heads=1,
                    concat=False,
                    dropout=dropout,
                    add_self_loops=False
                )

        }, aggr="sum")

        # -----------------------------------------
        # DROPOUT
        # -----------------------------------------

        self.dropout = nn.Dropout(
            dropout
        )

        # -----------------------------------------
        # FINAL CLASSIFIER
        # -----------------------------------------

        self.mlp = nn.Sequential(

            nn.Linear(
                hidden_dim,
                16
            ),

            nn.ReLU(),

            nn.Dropout(
                dropout
            ),

            nn.Linear(
                16,
                1
            )
        )

    # ---------------------------------------------
    # FORWARD PASS
    # ---------------------------------------------

    def forward(
        self,
        x_dict,
        edge_index_dict,
        touched_node_ids
    ):

        # -----------------------------------------
        # ENCODE ALL NODE TYPES
        # -----------------------------------------

        x_dict = {

            "inode":
                self.inode_encoder(
                    x_dict["inode"]
                ),

            "dirent":
                self.dirent_encoder(
                    x_dict["dirent"]
                ),

            "fd":
                self.fd_encoder(
                    x_dict["fd"]
                ),

            "link":
                self.link_encoder(
                    x_dict["link"]
                ),

            "rename":
                self.rename_encoder(
                    x_dict["rename"]
                )
        }

        # -----------------------------------------
        # GAT LAYER 1
        # -----------------------------------------

        x_dict = self.conv1(
            x_dict,
            edge_index_dict
        )

        x_dict = {
            key: self.dropout(
                torch.relu(value)
            )
            for key, value in x_dict.items()
        }

        # -----------------------------------------
        # GAT LAYER 2
        # -----------------------------------------

        x_dict = self.conv2(
            x_dict,
            edge_index_dict
        )

        x_dict = {
            key: torch.relu(value)
            for key, value in x_dict.items()
        }

        # -----------------------------------------
        # TOUCHED INODE EMBEDDINGS
        # -----------------------------------------

        inode_embeddings = (
            x_dict["inode"]
        )

        touched_embeddings = (
            inode_embeddings[
                touched_node_ids
            ]
        )

        # -----------------------------------------
        # MEAN POOLING
        # -----------------------------------------

        pooled = touched_embeddings.mean(
            dim=0
        )

        # -----------------------------------------
        # CLASSIFICATION
        # -----------------------------------------

        risk_logit = self.mlp(
            pooled
        )

        return risk_logit

    # ---------------------------------------------
    # PREDICT RISK
    # ---------------------------------------------

    def predict_risk(
        self,
        x_dict,
        edge_index_dict,
        touched_node_ids
    ):

        risk_logit = self.forward(
            x_dict,
            edge_index_dict,
            touched_node_ids
        )

        return torch.sigmoid(
            risk_logit
        )
