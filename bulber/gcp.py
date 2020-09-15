import os
from google.cloud import storage
from termcolor import colored
from bulber.params import MODEL_VERSION


def storage_upload(model_version=MODEL_VERSION, bucket=BUCKET_NAME, rm=False):
    client = storage.Client().bucket(bucket)
    storage_location = 'models/{}/versions/{}/{}'.format(
        MODEL_NAME,
        model_version,
        'model.bumbulb')
    blob = client.blob(storage_location)
    blob.upload_from_filename('bumbulb_VGG16_v4')
    print("=> model.bumbulb uploaded to bucket {} inside {}".format(BUCKET_NAME, storage_location))
    if rm:
        os.remove('model.bumbulb')
