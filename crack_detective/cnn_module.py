import time
import tensorflow as tf
import numpy as np
import pathlib as pl
from colorama import Fore, Style, init as colorama_init
from . import datasets as ds


from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.applications.vgg16 import VGG16
from tensorflow.keras.layers            import Activation, Conv2D, Dense, Dropout, Flatten, MaxPooling2D
from tensorflow.keras.layers.experimental.preprocessing  import Rescaling
from tensorflow.keras.models            import Model, Sequential
from tensorflow.keras.callbacks         import History


class Cnn(object):
    stats = None

    def __init__(self, width=224, height=224, channels=3, train_dataset=None, test_dataset=None, load=None):
        # self.train_dir = ds.datasets["Mendelay_1"]
        # self.test_dir = ds.datasets["Mendelay_1"]

        print(f"ENTER constructor for Cnn. Object is :{self.__class__.__name__}. kwargs:{(width, height)}")

        self.train_dir = train_dataset
        self.test_dir = test_dataset

        self.width = width
        self.height = height
        self.channels = channels

        self.stats = []

        print(f"self: w:{self.width}, h:{self.height}")

    def train(self, batch_size=32, epochs=5):
        train_datagen = ImageDataGenerator(rescale=1./255,
                                           shear_range=0.2,
                                           zoom_range=0.2,
                                           horizontal_flip=True,
                                           validation_split=0.2)

        train_generator = train_datagen.flow_from_directory(self.train_dir,
                                                            target_size=(self.width, self.height),
                                                            batch_size=batch_size,
                                                            class_mode='binary',)

        validation_generator = train_datagen.flow_from_directory(self.train_dir,
                                                                target_size=(self.width, self.height),
                                                                batch_size=batch_size,
                                                                class_mode='binary',)

        self.model.fit(
            train_generator,
            validation_data=validation_generator,
            epochs=epochs,
            steps_per_epoch=len(train_generator),
            validation_steps=len(validation_generator)
        )


    def save_model(self, path):
        self.model.save(path)

    def load_model(self, path):
        print(Fore.RED + f"Loading model: {path}" + Style.RESET_ALL)
        self.model = tf.keras.models.load_model(path)

    def predict(self, x, **kvargs):
        import time
        start = time.time()
        predictions=self.model.predict(x, **kvargs)
        stop = time.time()
        self.stats.append((predictions.shape[0], stop - start))
        # print(f"Measurement: {(predictions.shape[0], stop - start)}")
        return predictions



class CnnVgg16(Cnn):
    def __init__(self, **kvargs):
        super().__init__(**kvargs)

        self.vgg = VGG16(input_shape=[self.width, self.height, self.channels], weights='imagenet', include_top=False)

        for layer in self.vgg.layers:
            layer.trainable = False

        x = Flatten()(self.vgg.output)
        x = Dense(256, activation='relu')(x)
        x = Dropout(0.5)(x)
        x = Dense(1, activation='sigmoid')(x)

        self.model = Model(inputs=self.vgg.input, outputs=x)
        self.model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])



class CnnOriginal(Cnn):
    def __init__(self, **kvargs):
        super().__init__(**kvargs)

        # BUILD MODEL
        model = Sequential()
        model.add(Rescaling(1./255))

        model.add(Conv2D(16, (5, 5), input_shape = (self.width, self.height, self.channels)))
        model.add(Activation("relu"))
        model.add(MaxPooling2D(pool_size=(5, 5)))
        model.add(Dropout(0.2))

        model.add(Conv2D(32, (3, 3)))
        model.add(Activation("relu"))
        model.add(MaxPooling2D(pool_size=(3, 3)))
        model.add(Dropout(0.2))

        model.add(Conv2D(64, (2, 2)))
        model.add(Activation("relu"))
        model.add(MaxPooling2D(pool_size=(2, 2)))
        model.add(Dropout(0.2))

        model.add(Flatten())

        model.add(Dense(32))
        model.add(Activation("relu"))

        model.add(Dense(1))
        model.add(Activation('sigmoid'))

        self.model = model
        if kvargs.get("load"):
            self.load_model(kvargs["load"])


    def train(self, batch_size=64, epochs=20, **kvargs):
        split = 0.2
        seed_ = 333

        time_for_training = 0
        lr1 = 0.001
        lr2 = 0.0005 #default = 0.001
        lr3 = 0.00030326537671498954

        lr_ = lr1

        history = History()

        train_ds = tf.keras.preprocessing.image_dataset_from_directory(
            self.train_dir,
            validation_split=split,
            subset="training",
            seed=seed_,
            image_size=(self.height, self.width),
            batch_size=batch_size)

        val_ds = tf.keras.preprocessing.image_dataset_from_directory(
            self.train_dir,
            validation_split=split,
            subset="validation",
            seed=seed_,
            image_size=(self.height, self.width),
            batch_size=batch_size)

        # class_names = train_ds.class_names
        # print(class_names)

        def scheduler(epoch, lr):
            q, r = divmod(epoch, 10)
            # if r == 0 + 5:
            #     print("EPOCH: ", epoch, " LR: ", lr)
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
        self.model.compile(loss="binary_crossentropy",
                           optimizer=tf.keras.optimizers.Adam(learning_rate = lr_),
                           metrics=['accuracy'])

        self.model.fit(
            train_ds,
            validation_data=val_ds,
            batch_size=batch_size,
            epochs=epochs,
            callbacks=[lr_callback, history, train_Time]
            )
