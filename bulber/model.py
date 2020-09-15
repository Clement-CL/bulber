from __future__ import absolute_import
from tensorflow import keras
from tensorflow.keras.applications.vgg16 import VGG16
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Dropout, Activation, Flatten, Conv2D, MaxPooling2D
from tensorflow.keras import optimizers
from tensorflow.keras.applications.vgg16 import preprocess_input

def build_baseline_model():

    model = Sequential()
    model.add(Conv2D(30, (5,5), strides=(1,1), padding='valid', input_shape=(150, 150, 3), activation='relu'))
    model.add(MaxPooling2D(3))

    model.add(Conv2D(60, (2, 2), padding='same', activation='relu'))
    model.add(MaxPooling2D(3))

    model.add(Conv2D(50, (2, 2), padding='same', activation='relu'))
    model.add(MaxPooling2D(3))

    model.add(Flatten())
    model.add(Dense(25))
    model.add(Activation('softmax'))

    model.summary()

    return model

def transfer_VGG16(input_shape=None):
    print(input_shape)
    model = VGG16(weights="imagenet", include_top=False, input_shape=input_shape)
    # Set the first layers to be untrainable
    model.trainable = False
    # Add layers to the mdoel
    flatten_layer = Flatten()
    dense_layer = Dense(500, activation='relu')
    prediction_layer = Dense(25, activation='softmax')

    model = Sequential([model,
                        flatten_layer,
                        dense_layer,
                        prediction_layer])
    model.summary()

    return model
