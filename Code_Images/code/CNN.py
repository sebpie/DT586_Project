# -*- coding: utf-8 -*-
"""
Created on Mon May  3 18:20:17 2021

@author: eid
"""



import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras import layers
from tensorflow.keras.layers import Dense, Activation, Flatten, Conv2D, MaxPooling2D
from tensorflow.keras.callbacks import History
import matplotlib.pyplot as plt
import PIL
import PIL.Image
import numpy as np
import time
import pathlib
import os


CASE_0 = '64/'
CASE_1 = '64_INV/'
CASES = [CASE_0, CASE_1]

DataSourcePath = os.path.dirname(os.path.abspath(__name__))
# "C:/Users/eid/Desktop/Code_Images/"
print(f"Data source: {DataSourcePath}")
DATA_0 = 'Asphalt/'
DATA_1 = 'Bridge/'
DATA_2 = 'Mendelay_1/'
DATA_3 = 'Mendelay_2/'
DATA_4 = 'Private/'
DATA = [DATA_0, DATA_1, DATA_2, DATA_3, DATA_4]

IMG_STATE_1 ='Negative/'
IMG_STATE_2 = 'Positive/'
IMG_STATES = [IMG_STATE_1, IMG_STATE_2]


num_channels = 3
epochs_ = 20
data = DATA[4]
case = CASES[1]


def set_ups(size):
    
    # BUILD MODEL
    model = Sequential()
    model.add(layers.experimental.preprocessing.Rescaling(1./255))
    
    model.add(Conv2D(16, (5,5), input_shape = (size,size,num_channels)))
    model.add(Activation("relu"))
    model.add(MaxPooling2D(pool_size=(5,5)))
    model.add(layers.Dropout(0.2))
    
    model.add(Conv2D(32, (3,3)))
    model.add(Activation("relu"))
    model.add(MaxPooling2D(pool_size=(3,3)))
    model.add(layers.Dropout(0.2))
    
    model.add(Conv2D(64, (2,2)))
    model.add(Activation("relu"))
    model.add(MaxPooling2D(pool_size=(2,2)))
    model.add(layers.Dropout(0.2)) 
    
    model.add(Flatten())
    
    model.add(Dense(32))
    model.add(Activation("relu"))   
    
    model.add(Dense(1))
    model.add(Activation('sigmoid'))
    
    return model
    
    pass

def train(size, train_data, model):
    dataset_url = train_data
    data_dir = tf.keras.utils.get_file(origin=[], 
                                       fname=dataset_url, 
                                       extract=False)
    data_dir = pathlib.Path(data_dir)
    image_count = len(list(data_dir.glob('*/*.jpg')))
    print(image_count)

    #NAME = "Cracks-vs-No_cracks-CNN"

    batch_size_ = 64
    img_height = size
    img_width = size
#    num_channels = 3
    split = 0.2
    seed_ = 333

    time_for_training = 0
    lr1 = 0.001
    lr2 = 0.0005 #deafualt = 0.001
    lr3 = 0.00030326537671498954

    lr_ = lr1

    history = History()

    train_ds = tf.keras.preprocessing.image_dataset_from_directory(
      data_dir,
      validation_split=split,
      subset="training",
      seed=seed_,
      image_size=(img_height, img_width),
      batch_size=batch_size_)

    val_ds = tf.keras.preprocessing.image_dataset_from_directory(
      data_dir,
      validation_split=split,
      subset="validation",
      seed=seed_,
      image_size=(img_height, img_width),
      batch_size=batch_size_)

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
     #     return lr_
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
      batch_size=batch_size_,
      epochs=epochs_,
      callbacks=[lr_callback, history, train_Time]
      )


    print(history.history.keys())
    # visualizing losses and accuracy
    train_loss   = seqModel.history['loss']
    val_loss     = seqModel.history['val_loss']
    train_acc    = seqModel.history['accuracy']
    val_acc      = seqModel.history['val_accuracy']
#    learningRate = seqModel.history['lr']
    xc           = range(epochs_)




    return model, xc, train_acc, train_loss, val_acc, val_loss
    pass

    

def process_data(size, file):


    train_data = file
    
    model = set_ups(size)
    
    model, xc, train_acc, train_loss, train_val_acc, train_val_loss = train(size, train_data, model)
    
    acc = train_acc[epochs_ - 1]
    val_acc = train_val_acc[epochs_ - 1]
    loss = train_loss[epochs_ - 1]
    val_loss = train_val_loss[epochs_ - 1]
    time = time_for_training

    pass


file = os.path.join(DataSourcePath, data , case) 
print(f"file: {file}")
size = 64
process_data(size, file)

"""

for d in DATA:
    
    for c in CASES:
        

            
            file = DataSourcePath + d + c 
            print(file)
            
            size = 64
            
            process_data(size, file)

    pass

"""
print("END")
