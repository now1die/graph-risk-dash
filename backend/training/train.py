import torch

from training.dataset import (
    generate_dataset,
    split_dataset
)

from gnn.model import RiskGNN


# =====================================================
# SETTINGS
# =====================================================

LEARNING_RATE = 0.001

EPOCHS = 20


# =====================================================
# TRAINING
# =====================================================

def train_model():

    print()
    print("LOADING DATASET")
    print("----------------")

    dataset = generate_dataset()

    train_samples, validation_samples, test_samples = (
        split_dataset(dataset)
    )

    print(
        "Training samples:",
        len(train_samples)
    )

    print(
        "Validation samples:",
        len(validation_samples)
    )

    print(
        "Test samples:",
        len(test_samples)
    )

    print()

    # -------------------------------------------------
    # CREATE MODEL
    # -------------------------------------------------

    model = RiskGNN()

    # -------------------------------------------------
    # LOSS FUNCTION
    # -------------------------------------------------

    loss_function = torch.nn.BCEWithLogitsLoss()

    # -------------------------------------------------
    # OPTIMIZER
    # -------------------------------------------------

    optimizer = torch.optim.Adam(
        model.parameters(),
        lr=LEARNING_RATE
    )

    print("MODEL CREATED")
    print("-------------")
    print(model)

    print()
    print("STARTING TRAINING")
    print("-----------------")

    # -------------------------------------------------
    # TRAINING LOOP
    # -------------------------------------------------

    for epoch in range(1, EPOCHS + 1):

        model.train()

        total_loss = 0.0

        correct = 0
        total = 0

        for sample in train_samples:

            graph = sample["graph"]

            touched_inodes = sample["touched_inodes"]

            label = sample["label"]

            # -----------------------------------------
            # CLEAR OLD GRADIENTS
            # -----------------------------------------

            optimizer.zero_grad()

            # -----------------------------------------
            # GNN FORWARD PASS
            # -----------------------------------------

            output = model(
                graph,
                graph.x_dict,
                touched_inodes
            )

            # -----------------------------------------
            # CREATE LABEL TENSOR
            # -----------------------------------------

            target = torch.tensor(
                [float(label)]
            )

            # -----------------------------------------
            # CALCULATE LOSS
            # -----------------------------------------

            loss = loss_function(
                output,
                target
            )

            # -----------------------------------------
            # BACKPROPAGATION
            # -----------------------------------------

            loss.backward()

            # -----------------------------------------
            # UPDATE MODEL WEIGHTS
            # -----------------------------------------

            optimizer.step()

            # -----------------------------------------
            # TRACK LOSS
            # -----------------------------------------

            total_loss += loss.item()

            # -----------------------------------------
            # TRACK TRAINING ACCURACY
            # -----------------------------------------

            probability = torch.sigmoid(
                output
            ).item()

            prediction = 1 if probability >= 0.5 else 0

            if prediction == label:
                correct += 1

            total += 1

        average_loss = (
            total_loss /
            len(train_samples)
        )

        accuracy = (
            correct /
            total
        )

        print(
            "Epoch",
            epoch,
            "| Loss:",
            round(average_loss, 4),
            "| Accuracy:",
            round(accuracy, 4)
        )

    print()
    print("TRAINING COMPLETE")
    print("-----------------")

    return model


# =====================================================
# RUN TRAINING
# =====================================================

if __name__ == "__main__":

    trained_model = train_model()

    print()
    print("TRAINING TEST COMPLETE")
