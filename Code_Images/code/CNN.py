# -*- coding: utf-8 -*-
"""
Created on Mon May  3 18:20:17 2021
Modified on Thu Feb 8 20:13:32 2024

@author: eid, seb
"""


import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras import layers
from tensorflow.keras.layers import Dense, Activation, Flatten, Conv2D, MaxPooling2D
from tensorflow.keras.callbacks import History
import time
import pathlib
import os


CASE_0 = '64/'
CASE_1 = '64_INV/'
CASES = [CASE_0, CASE_1]

# Datasets are in the parent directory.
DataSourcePath = pathlib.Path(__file__).parent.parent.resolve()
# "C:/Users/eid/Desktop/Code_Images/"
print(f"Data source: {DataSourcePath}")

datasets = {}

def _add_dataset(name, *paths):
  global datasets
  datasets[name] = os.path.join(DataSourcePath, *paths )

_add_dataset('Asphalt', 'Asphalt/', '64')
_add_dataset('Asphalt_INV', 'Asphalt/', '64_INV/')
_add_dataset('Bridge', 'Bridge/', '64')
_add_dataset('Bridge_INV', 'Bridge', '64_INV')
_add_dataset('Mendelay_1', 'Mendelay_1', '64')
_add_dataset('Mendelay_1_INV', 'Mendelay_1', '64_INV')
_add_dataset('Mendelay_2', 'Mendelay_2', '64')
_add_dataset('Mendelay_2_INV', 'Mendelay_2', '64_INV')
_add_dataset('Private', 'Private', '64')
_add_dataset('Private', 'Private', 'INV')
_add_dataset('Mendelay_FULL', 'Mendelay_FULL')


# DATA_0 = 'Asphalt/'
# DATA_1 = 'Bridge/'
# DATA_2 = 'Mendelay_1/'
# DATA_3 = 'Mendelay_2/'
# DATA_4 = 'Private/'
# DATA_5 = 'Mendelay_FULL'
# DATA = [DATA_0, DATA_1, DATA_2, DATA_3, DATA_4, DATA_5]

IMG_STATE_1 ='Negative/'
IMG_STATE_2 = 'Positive/'
IMG_STATES = [IMG_STATE_1, IMG_STATE_2]


num_channels = 3
# data = DATA[4]
# case = CASES[1]


def setup(size=64):

    # BUILD MODEL
    model = Sequential()
    model.add(layers.experimental.preprocessing.Rescaling(1./255))

    model.add(Conv2D(16, (5, 5), input_shape = (size, size, num_channels)))
    model.add(Activation("relu"))
    model.add(MaxPooling2D(pool_size=(5, 5)))
    model.add(layers.Dropout(0.2))

    model.add(Conv2D(32, (3, 3)))
    model.add(Activation("relu"))
    model.add(MaxPooling2D(pool_size=(3, 3)))
    model.add(layers.Dropout(0.2))

    model.add(Conv2D(64, (2, 2)))
    model.add(Activation("relu"))
    model.add(MaxPooling2D(pool_size=(2, 2)))
    model.add(layers.Dropout(0.2))

    model.add(Flatten())

    model.add(Dense(32))
    model.add(Activation("relu"))

    model.add(Dense(1))
    model.add(Activation('sigmoid'))

    return model


def train(train_data, model, size=64, batch_size=64, epochs=20):
    print(f"Training model with dataset in {train_data}")
    data_dir = tf.keras.utils.get_file(origin=[],
                                       fname=train_data,
                                       extract=False)
    data_dir = pathlib.Path(data_dir)
    image_count = len(list(data_dir.glob('*/*.jpg')))
    print(f"image_count: {image_count}")

    img_height = size
    img_width = size
#    num_channels = 3
    split = 0.2
    seed_ = 333

    time_for_training = 0
    lr1 = 0.001
    lr2 = 0.0005 #default = 0.001
    lr3 = 0.00030326537671498954

    lr_ = lr1

    history = History()

    train_ds = tf.keras.preprocessing.image_dataset_from_directory(
      data_dir,
      validation_split=split,
      subset="training",
      seed=seed_,
      image_size=(img_height, img_width),
      batch_size=batch_size)

    val_ds = tf.keras.preprocessing.image_dataset_from_directory(
      data_dir,
      validation_split=split,
      subset="validation",
      seed=seed_,
      image_size=(img_height, img_width),
      batch_size=batch_size)

    class_names = train_ds.class_names
    print(class_names)

    def scheduler(epoch, lr):
      q, r = divmod(epoch, 10)
      if r == 0 + 5:
         print("EPOCH: ", epoch, " LR: ", lr)
      if epoch <= 10:
        return lr1
      elif epoch < 40:
          return lr2
      elif epoch < 50:
          return lr3
      else:
          return lr * tf.math.exp(-0.1)


    lr_callback = tf.keras.callbacks.LearningRateScheduler(scheduler)

    class TrainTime(tf.keras.callbacks.Callback):
        def on_train_begin(self, logs=None):
            print("TRAIN BEGINS")
            self.train_time_start = time.time()

        def on_train_end(self, logs=None):
            global time_for_training
            self.train_time = (time.time() - self.train_time_start)
            print("TRAIN TIME: ", self.train_time)
            time_for_training = self.train_time

    train_Time = TrainTime()


    # COMPILE MODEL
    model.compile(loss="binary_crossentropy",
                  optimizer=tf.keras.optimizers.Adam(learning_rate = lr_),
                  metrics=['accuracy'])

    seqModel = model.fit(
      train_ds,
      validation_data=val_ds,
      batch_size=batch_size,
      epochs=epochs,
      callbacks=[lr_callback, history, train_Time]
      )


    print(f"History: {history.history.keys()}")
    # visualizing losses and accuracy
    train_loss   = seqModel.history['loss']
    val_loss     = seqModel.history['val_loss']
    train_acc    = seqModel.history['accuracy']
    val_acc      = seqModel.history['val_accuracy']
#    learningRate = seqModel.history['lr']
    xc           = range(epochs)


    return model, history, seqModel


def process_data(train_data, size=64, epochs=20):

    model = setup(size)

    model, xc, train_acc, train_loss, train_val_acc, train_val_loss = train(size=size, train_data=train_data, model=model, epochs=epochs)

    acc = train_acc[epochs - 1]
    val_acc = train_val_acc[epochs - 1]
    loss = train_loss[epochs - 1]
    val_loss = train_val_loss[epochs - 1]
    time = time_for_training

    return model


def plot(history):
  import pandas as pd
  import matplotlib.pyplot as plt

  pd.DataFrame(history.history).plot(figsize=(8,5))
  plt.grid(True)
  plt.gca().set_ylim(0,1)
  plt.show()