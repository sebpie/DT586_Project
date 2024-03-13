import argparse
from . import cnn_module as cnn
from .datasets import datasets

def main(args):

    if args.train_set not in datasets.keys():
        raise ValueError(f"Dataset {args.train_set} not found.")
    train_dataset = datasets[args.train_set]

    args.train_dataset = train_dataset
    args.test_dataset = train_dataset

    match(args.cnn):
        case "VGG16":
            model = cnn.CnnVgg16(width=args.size,
                        height=args.size,
                        train_dataset=train_dataset,
                        test_dataset =train_dataset
                        )

        case "Orig" :
            model = cnn.CnnOriginal(width=args.size,
                        height=args.size,
                        train_dataset=train_dataset,
                        test_dataset =train_dataset
                        )

    print(f"model is {model.__class__.__name__}")

    model.train(batch_size=args.batch_size,
                epochs=args.epochs)

    if args.save:
        model.save_model(args.save)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--cnn', type=str, default="VGG16", choices=["VGG16", "Orig"], help="Name of the CNN.")
    parser.add_argument('--size', type=int, default=224, help="Build model with image of size x size pixels.")
    parser.add_argument('--epochs', type=int, default=5, help="Number of epochs.")
    parser.add_argument('--batch_size', type=int, default=64, help="Batch size of each training step.")
    parser.add_argument('--load', type=str, help="Load pre-trained model.")
    parser.add_argument('--save', type=str, help="Train and save model to file.")
    parser.add_argument('--train_set', default="Mendelay_FULL", help="Name of dataset to train the model with.")

    args = parser.parse_args()
    main(args)
