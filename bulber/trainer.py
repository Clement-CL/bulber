from __future__ import absolute_import

import multiprocessing
import time
import warnings
from tempfile import mkdtemp

import pandas as pd
import numpy as np
from memoized_property import memoized_property

from bulber.utils import simple_time_tracker
from bulber.model import build_baseline_model, transfer_VGG16
# from bulber.gcp import storage_upload
from bulber.params import MODEL_VERSION
from bulber.data import get_data

from tensorflow.keras.callbacks import EarlyStopping, TensorBoard
from tensorflow.keras import optimizers
from tensorflow.keras.applications.vgg16 import preprocess_input
import tensorflow_cloud as tfc

from google.cloud import storage

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelBinarizer

from joblib import dump, load

class Trainer:

    def __init__(self, X, y, X_augmented, y_augmented, estimator='VGG16', **kwargs):
        self.kwargs = kwargs

        self.X = preprocess_input(X)
        self.X_augmented = preprocess_input(X_augmented)
        self.y = y
        self.y_augmented = y_augmented

        self.X_train, self.X_test, self.y_train, self.y_test = train_test_split(X, y, test_size=0.3, random_state=1)

        self.input_shape = self.X_train[0].shape
        self.opt = None
        self.estimator = estimator
        self.experiment_name = 'bumbulb_v5'


    def get_estimator(self):
        if self.estimator == 'baseline':
            model = build_baseline_model()
            model.compile(loss='categorical_crossentropy',
                          optimizer='adam',
                          metrics=['accuracy'])

        if self.estimator == 'VGG16':
            model = transfer_VGG16(input_shape=self.input_shape)
            self.opt = optimizers.Adam(learning_rate=1e-4)
            model.compile(loss='categorical_crossentropy',
                          optimizer=self.opt,
                          metrics=['accuracy'])

        return model

    @simple_time_tracker
    def train(self):
        tic = time.time()
        # add augmented images
        X_train = np.vstack((self.X_train, self.X_augmented))
        y_train = np.concatenate((self.y, self.y_augmented), axis=None)

        # fit encoder on y_train
        self.label_enc = LabelBinarizer()
        self.label_enc.fit(y_train)

        dump(self.label_enc, 'label_encoder.joblib')
        print(self.label_enc.classes_)
        y_train_enc = self.label_enc.transform(y_train)
        # set callbacks
        es = EarlyStopping(monitor='val_loss', mode='min', patience=3, verbose=1, restore_best_weights=True)
        # log_dir = "logs/fit/" + datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
        # board = TensorBoard(log_dir=tensorboard_path, histogram_freq=1)
        model = self.get_estimator()

        # fit model with new X_train
        model.fit(X_train, y_train_enc, validation_split=0.3,
                    epochs=10,
                    batch_size=16,
                    callbacks=[es])

        return model

    def evaluate(self, model, show=False):

        # get predictions for all species
        y_pred = model.predict(self.X_test)
        columns = self.label_enc.classes_
        y_pred_df = pd.DataFrame(y_pred, columns=columns)

        # get species with top prediction and true species
        y_pred_df['pred_species'] = y_pred_df.idxmax(axis=1)
        y_pred_df['true_species'] = self.y_test

        # measure success rate
        prediction_review = (y_pred_df['pred_species'] == y_pred_df['true_species'])
        accuracy = prediction_review.value_counts()[True] / prediction_review.count()
        print(f'test accuracy: {accuracy}')

    def save_model(self,model, local=True):
        if local:
            model.save(MODEL_VERSION)
        # else: placeholder for API run

    def evaluate_saved_model(self, model=MODEL_VERSION):
        reconstructed_model = load_model(model)
        y_pred_recon = reconstructed_model.predict(self.X_test)
        label_enc = load('label_enc.joblib')
        columns = label_enc.classes_
        y_pred_recon_df = pd.DataFrame(y_pred_recon)
        print(y_pred_recon_df)

if __name__ == "__main__":
    warnings.simplefilter(action='ignore', category=FutureWarning)
    # Get and clean data
    experiment = "bumbulb_v5"
    print("############   Loading Data   ############")
    X, y, X_augmented, y_augmented = get_data(nrows=800)
    print(len(X), len(y), len(X_augmented), len(y_augmented))
    # instenciate Trainer()
    t = Trainer(X, y, X_augmented, y_augmented)
    print("############  Training model   ############")
    model = t.train()
    print("############  Evaluating model ############")
    t.evaluate(model)
    # print("############   Saving model    ############")

    # t.save_model(model)
    # print("############   Test saved model    ############")
    # t.evaluate_saved_model()



