import tensorflow as tf
import numpy as np
import pathlib as pl
from colorama import Fore, Style
import datasets as ds


from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.applications.vgg16 import VGG16
from tensorflow.keras.layers import Dense, Flatten, Dropout
from tensorflow.keras.models import Model

class Cnn():
    def __init__(self):
        self.train_dir = ds.datasets["Mendelay_1"]
        self.test_dir = ds.datasets["Mendelay_1"]

    def train_model(self):
        pass

    def save_model(self, path):
        self.model.save(path)

    def load_model(self, path):
        self.model = tf.keras.models.load_model(path)
        print(path)

    def predict(self):
        pass

class CnnOriginal(Cnn):
    pass


class CnnVgg16(Cnn):
    def __init__(self, width=224, height=224, channels=3):
        super().__init__()
        self.width = width
        self.height = height
        self.channels = channels


        self.vgg = VGG16(input_shape=[self.width, self.height, self.channels], weights='imagenet', include_top=False)

        for layer in self.vgg.layers:
            layer.trainable = False

        x = Flatten()(self.vgg.output)
        x = Dense(256, activation='relu')(x)
        x = Dropout(0.5)(x)
        x = Dense(1, activation='sigmoid')(x)

        self.model = Model(inputs=self.vgg.input, outputs=x)
        self.model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])

    def train_model(self):
        train_datagen = ImageDataGenerator(rescale=1./255,
                                           shear_range=0.2,
                                           zoom_range=0.2,
                                           horizontal_flip=True,
                                           validation_split=0.2)

        train_generator = train_datagen.flow_from_directory(self.train_dir, target_size=(224,224),
                                                            batch_size=32,
                                                            class_mode='binary',)

        validation_generator = train_datagen.flow_from_directory(self.train_dir, target_size=(224,224),
                                                                batch_size=32,
                                                                class_mode='binary',)

        self.model.fit(
            train_generator,
            validation_data=validation_generator,
            epochs=5,
            steps_per_epoch=len(train_generator),
            validation_steps=len(validation_generator)
        )

    # def predict(self, img_array): #fix this
    #     for file in pl.Path(self.test_dir, "Positive").iterdir(): #put in another function
    #         img = tf.keras.preprocessing.image.load_img(file, target_size=(224,224))
    #         img_array = tf.keras.preprocessing.image.img_to_array(img)
    #         img_array = tf.expand_dims(img_array, 0)
    #         prediction = self.model.predict(img_array)[0][0]

    #         if prediction > 0.5:
    #             print(Fore.GREEN + f"{file.name} is a crack {prediction}")
    #         else:
    #             print(Fore.RED + f"{file.name} is not a crack {prediction}")


#______________
# results = predict (npArray)
    def predict(self, img_array): #fix this
        prediction = self.model.predict(img_array)[0][0]
        if prediction > 0.5:
            print('crack_detected')
        else:
            print('no crack_detected')


print("model loaded successfully!")