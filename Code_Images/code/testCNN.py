import CNN

import argparse
import keras
import pathlib
import numpy as np

from colorama import Fore, Style
from keras import Model

test_dir = CNN.datasets["Mendelay_2"]
print(f"test_dir: {test_dir}")


def load_imgdir(*path, target_size=(80, 80)):
    pixels = []
    print(f"path: {path, *path}")
    for file in pathlib.Path(*path).iterdir():
        # print(f"Analysing file: {file}")
        img = keras.utils.load_img(file, target_size=target_size)

        img_array = keras.utils.img_to_array(img)
        pixels.append(img_array)
    return np.array(pixels)

def main(args):

    if args.train_set not in CNN.datasets.keys():
        raise ValueError(f"Dataset {args.train_set} not found.")
    train_dataset = CNN.datasets[args.train_set]


    model:Model = CNN.setup(size=args.size)

    CNN.train(model=model,
              train_data = train_dataset,
              batch_size=args.batch_size,
              epochs=args.epochs)

    if args.save:
        model.save(args.save)

    # x = load_imgdir(test_dir, "Positive")
    # prediction = model.predict(x)
    # print(f"Prediction: {prediction}")

    # for crack_detected in prediction:
    #     if(crack_detected > 0.95):
    #         colour = Fore.GREEN
    #     elif(crack_detected > 0.5):
    #         colour = Fore.YELLOW
    #     else:
    #         colour = Fore.RED

    #     print(f"{colour}{file}{Style.RESET_ALL} [{crack_detected}]. Class: {np.argmax( crack_detected, axis=1)}")


    for file in pathlib.Path(test_dir, "Positive").iterdir():
        # print(f"Analysing file: {file}")
        img = keras.utils.load_img(file, target_size=(args.size, args.size))

        img_array = keras.utils.img_to_array(img)
        # print(f"img: {img} | img_array: {img_array}")
        x = np.expand_dims(img_array, axis=0)
        crack_detected = model.predict(x)

        # print(f"{file}: {crack_detected}")
        if(crack_detected > 0.95):
            colour = Fore.GREEN
        elif(crack_detected > 0.5):
            colour = Fore.YELLOW
        else:
            colour = Fore.RED

        print(f"{colour}{file}{Style.RESET_ALL} [{crack_detected}]. Class: {np.argmax( crack_detected, axis=1)}")


    # img = keras.utils.load_img("PetImages/Cat/6779.jpg", target_size=image_size)
    # plt.imshow(img)

    # img_array = keras.utils.img_to_array(img)
    # img_array = keras.ops.expand_dims(img_array, 0)  # Create batch axis

    # predictions = model.predict(img_array)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--size', type=int, default=80, help="Build model with image of size x size pixels.")
    parser.add_argument('--epochs', type=int, default=5, help="Number of epochs.")
    parser.add_argument('--batch_size', type=int, default=64, help="Batch size of each training step.")
    parser.add_argument('--load', type=str, help="Load pre-trained model.")
    parser.add_argument('--save', help="Train and save model to file.")
    parser.add_argument('--train_set', default="Mendelay_FULL", help="Name of dataset to train the model with.")

    args = parser.parse_args()
    main(args)
