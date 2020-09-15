import pandas as pd
import numpy as np
import csv
import os
from PIL import Image
import glob
from sklearn.model_selection import train_test_split
# from bulber.params import BUCKET_NAME
from google.cloud import storage
import requests
from io import BytesIO

path_csv = '/Users/clementchausserie-lapree/code/Clement-CL/bulber/data/bumbulb_img_v2.csv'
path_images = '/Users/clementchausserie-lapree/code/Clement-CL/bulber/data/images/images_originals/'
path_augmented = '/Users/clementchausserie-lapree/code/Clement-CL/bulber/data/image_augmented.csv'
path_images_augmented = '/Users/clementchausserie-lapree/code/Clement-CL/bulber/data/images/images_augmented/'

def get_data(nrows=500, local=True):

    # client = storage.Client()
    # bucket = client.bucket(BUCKET_NAME)
    # blobs=list(bucket.list_blobs())

    X_list = []
    y_list = []
    # angle_list = []

    X_list_augmented = []
    y_list_augmented = []

    i = 0

    if local:
        # load dataframe with all images
        bumbulb_images = pd.read_csv(path_csv)
        augmented_images = pd.read_csv(path_augmented)
        if nrows is not None:
            bumbulb_images = bumbulb_images.sample(n=nrows)
            augmented_images = augmented_images.sample(n=nrows)
        # iterate through the list to extract images and save them as arrays in an X and y list.
        # create an angle list to review predictions
        for index, rows in bumbulb_images.iterrows():
            pic = np.array(Image.open(f'{path_images}{rows.image_title}.jpg'))
            X_list.append(pic)
            y_list.append(rows.species)
        for index, rows in augmented_images.iterrows():
            pic_aug = np.array(Image.open(f'{path_images_augmented}{rows.augmented_images}'))
            X_list_augmented.append(pic_aug)
            y_list_augmented.append(rows.augmented_species)
            # angle_list.append(rows.angle)

    else:
        for blob in blobs:
            blob_name = blob.name
            if 'jpg' in blob_name:
                img_name = blob_name.split("_")[0].split("/")[1]
                # angle = blob_name.split("_")[1]
                blob_0 = bucket.blob(blob_name)
                pic = f"{'_'.join(img_name.split(' '))}_{i}.jpg"
                blob_0.download_to_filename(pic)
                img_0 = np.asarray(Image.open(pic))
                X_list.append(img_0)
                y_list.append(img_name)
                # angle_list.append(angle)
                i += 1
                os.remove(pic)
            # if 'augmented' in blob_name:
            #     img_name = blob_name.split("_")[0].split("/")[1]
            #     # angle = blob_name.split("_")[1]
            #     blob_0 = bucket.blob(blob_name)
            #     pic = f"{'_'.join(img_name.split(' '))}_{i}.jpg"
            #     blob_0.download_to_filename(pic)
            #     img_0 = np.asarray(Image.open(pic))
            #     X_list_augmented.append(img_0)
            #     y_list_augmented.append(img_name)
            #     # angle_list.append(angle)
            #     i += 1
            #     os.remove(pic)

    # create X and y
    X = np.stack(X_list, axis=0)
    y = np.stack(y_list, axis=0)
    X_augmented = np.stack(X_list_augmented, axis=0)
    y_augmented = np.stack(y_list_augmented, axis=0)

    # check number of dimensions

    assert X.ndim == 4
    assert y.ndim == 1

    assert X_augmented.ndim == 4
    assert y_augmented.ndim == 1
    print(X.ndim, X_augmented.ndim)

    return X, y, X_augmented, y_augmented

if __name__ == "__main__":
    X, y, X_augmented, y_augmented = get_data()
    # print(X.shape, y.shape)
