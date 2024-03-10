from PIL import Image
import numpy as np
import cnn_module as cnn
import tensorflow as tf

import pathlib as pl
from colorama import Fore, Style
import CNN
import os

#instantiate the model
model = cnn.CnnVgg16()

#model.train_model()

test_dir = CNN.datasets["Mendelay_1"]

#load one file from the test directory
file = pl.Path(test_dir,"Positive").iterdir()


file_path = os.path.join(os.path.dirname(__file__), '00007.jpg')
img = tf.keras.preprocessing.image.load_img(file_path, target_size=(224, 224))
img_array = tf.keras.preprocessing.image.img_to_array(img)
img_array = tf.expand_dims(img_array, 0)

# img = Image.open('00001.jpg')
# np_img = np.array(image)

model.predict(img_array)






# results = model.predict(np_img)

#print(model.width)


##load files and prepare images for model submission.

#load files and prepare images for model submission.
# img = tf.keras.preprocessing.image.load_img(img, target_size=(224,224))
# image_array = tf.keras.preprocessing.image.img_to_array(img)
# image_array = tf.expand_dims(image_array, 0)