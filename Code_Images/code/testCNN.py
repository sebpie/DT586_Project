import CNN
import os
import pathlib

from colorama import Fore, Style
from tensorflow.keras import Model
from PIL import Image
import numpy
import keras

test_dir = os.path.join(CNN.get_dataset_dir(CNN.DATA_1), CNN.IMG_STATE_2)


def main():
    model:Model = CNN.setup()
    dataset_dir = CNN.get_dataset_dir(CNN.DATA_3)
    CNN.train(model=model, train_data = dataset_dir, batch_size=16, epochs=20)


    for file in pathlib.Path(test_dir).iterdir():
        # print(f"Analysing file: {file}")
        img = keras.utils.load_img(file, target_size=(64, 64))

        img_array = keras.utils.img_to_array(img)

        x = numpy.expand_dims(img_array, axis=0)
        crack_detected = model.predict(x)

        # print(f"{file}: {crack_detected}")
        if(crack_detected > 0.95):
            colour = Fore.GREEN
        elif(crack_detected > 0.5):
            colour = Fore.YELLOW
        else:
            colour = Fore.RED


        print(f"{colour}{file}{Style.RESET_ALL} [{crack_detected}]")


    # img = keras.utils.load_img("PetImages/Cat/6779.jpg", target_size=image_size)
    # plt.imshow(img)

    # img_array = keras.utils.img_to_array(img)
    # img_array = keras.ops.expand_dims(img_array, 0)  # Create batch axis

    # predictions = model.predict(img_array)


if __name__ == "__main__":
    main()
