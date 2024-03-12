from PIL import Image
import numpy as np
import cnn_module as cnn
import tensorflow as tf
import pathlib as pl
from colorama import Fore, Style
import datasets as ds
import os
import scipy

#instantiate the model
model = cnn.CnnVgg16()
#model.train_model()

pat = os.path.abspath('test101.keras')
model.load_model(pat)

test_dir = ds.datasets["Mendelay_1"]

#load one file from the test directory
file_path = os.path.join(os.path.dirname(__file__), '00007.jpg')
img = tf.keras.preprocessing.image.load_img(file_path, target_size=(224, 224))
img_array = tf.keras.preprocessing.image.img_to_array(img)
img_array = tf.expand_dims(img_array, 0)


model.predict(img_array)


#train and save the model
# model.train_model()
# model.save_model('test101.keras')

#load the model and predict
# model.load_model()

#preprocess the imae


# model.predict()


#try to load model if fail train model and reload if succeed use model to predict
