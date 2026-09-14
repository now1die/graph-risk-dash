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

        # -----------------------------------------
        # FIRST GAT LAYER
        # -----------------------------------------

        self.conv1 = HeteroConv({

            ("inode", "contains", "dirent"):
                GATConv(
                    (hidden_dim, hidden_dim),
                    hidden_dim,
                    heads=heads,
                    concat=True,
                    dropout=dropout,
                    add_self_loops=False
                ),

            ("dirent", "points_to", "inode"):
                GATConv(
                    (hidden_dim, hidden_dim),
                    hidden_dim,
                    heads=heads,
                    concat=True,
                    dropout=dropout,
                    add_self_loops=False
                ),

            ("inode", "links", "inode"):
                GATConv(
                    (hidden_dim, hidden_dim),
                    hidden_dim,
                    heads=heads,
                    concat=True,
                    dropout=dropout,
                    add_self_loops=False
                ),

            ("fd", "open_by", "inode"):
                GATConv(
                    (hidden_dim, hidden_dim),
                    hidden_dim,
                    heads=heads,
                    concat=True,
                    dropout=dropout,
                    add_self_loops=False
                ),

            ("inode", "opened_by", "fd"):
                GATConv(
                    (hidden_dim, hidden_dim),
                    hidden_dim,
                    heads=heads,
                    concat=True,
                    dropout=dropout,
                    add_self_loops=False
                ),

            ("inode", "renames", "inode"):
                GATConv(
                    (hidden_dim, hidden_dim),
                    hidden_dim,
                    heads=heads,
                    concat=True,
                    dropout=dropout,
                    add_self_loops=False
                )

        }, aggr="sum")

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

            ("inode", "links", "inode"):
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

            ("inode", "renames", "inode"):
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

        self.dropout = nn.Dropout(dropout)

        # -----------------------------------------
        # CLASSIFIER
        # -----------------------------------------

        self.mlp = nn.Sequential(
            nn.Linear(hidden_dim, 16),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(16, 1)
        )

    # ---------------------------------------------
    # FORWARD
    # ---------------------------------------------

    def forward(
        self,
        x_dict,
        edge_index_dict,
        touched_node_ids
    ):

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
                )
        }

        # GAT layer 1
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

        # GAT layer 2
        x_dict = self.conv2(
            x_dict,
            edge_index_dict
        )

        x_dict = {
            key: torch.relu(value)
            for key, value in x_dict.items()
        }

        # Touched inode embeddings
        inode_embeddings = x_dict["inode"]

        touched_embeddings = inode_embeddings[
            touched_node_ids
        ]

        # Mean pooling
        pooled = touched_embeddings.mean(
            dim=0
        )

        # Risk logit
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
