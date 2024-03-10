# import tensorflow as tf
# import numpy as np
# import pathlib as pl
# from colorama import Fore, Style

# from tensorflow.keras.preprocessing.image import ImageDataGenerator
# from tensorflow.keras.applications.vgg16 import VGG16
# from tensorflow.keras.layers import Dense, Flatten, Dropout
# from tensorflow.keras.models import Model

# #load VGG16 model without top fully connected layers
# vgg = VGG16(input_shape=[224,224,3], weights='imagenet', include_top=False)

# #Frees pretrained layers so that they are not trained again
# for layer in vgg.layers:
#     layer.trainable = False

# #Add custom layer for crack detection in images of concrete
# x = Flatten()(vgg.output)
# x = Dense(256, activation='relu')(x)
# x = Dropout(0.5)(x)
# x = Dense(1, activation='sigmoid')(x)

# #Combine VGG16 model with custom layers
# model = Model(inputs=vgg.input, outputs=x)
# #print(model.summary())

# #Compile the model
# model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])

# #import datasets from CNN class (Sebastian & Daniel code)
# import CNN
# train_dir = CNN.datasets["Mendelay_1"]
# test_dir = CNN.datasets["Mendelay_1"]

# #Data generation for training and validation data
# train_datagen = ImageDataGenerator(rescale=1./255,
#                                    shear_range=0.2,
#                                    zoom_range=0.2,
#                                    horizontal_flip=True,
#                                    validation_split=0.2)

# train_generator = train_datagen.flow_from_directory(train_dir, target_size=(224,224),
#                                                     batch_size=32,
#                                                     class_mode='binary',)

# validation_generator = train_datagen.flow_from_directory(train_dir, target_size=(224,224),
#                                                          batch_size=32,
#                                                          class_mode='binary',)

# #Model training
# predict = model.fit(
#     train_generator,
#     validation_data=validation_generator,
#     epochs=5,
#     steps_per_epoch=len(train_generator),
#     validation_steps=len(validation_generator)
# )

# #loop through the test directory and predict the images
# for file in pl.Path(test_dir,"Negative").iterdir():
#     img = tf.keras.preprocessing.image.load_img(file, target_size=(224,224))
#     img_array = tf.keras.preprocessing.image.img_to_array(img)
#     img_array = tf.expand_dims(img_array, 0)
#     prediction = model.predict(img_array)[0][0]

#     #print the prediction if accuracy is greater than 90% print green
#     #esle if greater that 50% print yellow else print red


#     if prediction > 0.9:
#         print(Fore.GREEN + f"{file.name} is a crack{prediction}")
#     elif prediction > 0.5:
#         print(Fore.YELLOW + f"{file.name} is a crack{prediction}")
#     else:
#         print(Fore.RED + f"{file.name} is not a crack{prediction}")

import tensorflow as tf
import numpy as np
import pathlib as pl
from colorama import Fore, Style

from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.applications.vgg16 import VGG16
from tensorflow.keras.layers import Dense, Flatten, Dropout
from tensorflow.keras.models import Model


vgg = VGG16(input_shape=[224,224,3], weights='imagenet', include_top=False)


for layer in vgg.layers:
    layer.trainable = False


x = Flatten()(vgg.output)
x = Dense(256, activation='relu')(x)
x = Dropout(0.5)(x)
# Use 'sigmoid' activation for binary classification
x = Dense(1, activation='sigmoid')(x)


model = Model(inputs=vgg.input, outputs=x)
#print(model.summary())


model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])


import CNN
train_dir = CNN.datasets["Mendelay_1"]
test_dir = CNN.datasets["Mendelay_1"]


train_datagen = ImageDataGenerator(rescale=1./255,
                                   shear_range=0.2,
                                   zoom_range=0.2,
                                   horizontal_flip=True,
                                   validation_split=0.2)

train_generator = train_datagen.flow_from_directory(train_dir, target_size=(224,224),
                                                    batch_size=32,
                                                    class_mode='binary',) # Change class_mode to 'binary'

validation_generator = train_datagen.flow_from_directory(train_dir, target_size=(224,224),
                                                         batch_size=32,
                                                         class_mode='binary',) # Change class_mode to 'binary'


predict = model.fit(
    train_generator,
    validation_data=validation_generator,
    epochs=5,
    steps_per_epoch=len(train_generator),
    validation_steps=len(validation_generator)
)


for file in pl.Path(test_dir,"Positive").iterdir():
    img = tf.keras.preprocessing.image.load_img(file, target_size=(224,224))
    img_array = tf.keras.preprocessing.image.img_to_array(img)
    img_array = tf.expand_dims(img_array, 0)
    prediction = model.predict(img_array)[0][0]

    # Use 0.5 threshold for binary classification
    if prediction > 0.5:
        print(Fore.GREEN + f"{file.name} is a crack {prediction}")
    else:
        print(Fore.RED + f"{file.name} is not a crack {prediction}")
