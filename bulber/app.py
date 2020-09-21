import streamlit as st
from PIL import Image
from resizeimage import resizeimage
from bulber.data import get_data
from sklearn.preprocessing import LabelEncoder
import numpy as np
import pandas as pd
from tensorflow.keras.models import load_model
from tensorflow.keras.applications.vgg16 import preprocess_input
from joblib import load

import time

# import required csvs

plants_full_info_df = pd.read_csv('data/all_species_care.csv')
image_urls = pd.read_csv('data/links_to_images.csv').set_index('Species')


# Page formatting and image display

st.set_option('deprecation.showfileUploaderEncoding', False)
st.markdown("<h1 style='text-align: left; color: red;'img/h1>", unsafe_allow_html=True)
img = st.image('data/logo.png', width=400, output_format='png')

st.header('Welcome to Bulber !')
st.write('')
st.subheader('We will identify the plant of your dreams, and return your compatibility.')
st.write('Follow the instructions below to get started.')
st.write('')
st.write('')

# Follow the instructions below to get started
# User defined inputs with dropdown menus

st.markdown('**Please describe the room conditions for the plant**')

display = ("Click me",
           "Little sun",
           "Medium sun",
           "Full sun")

options = list(range(len(display)))
value_light = st.selectbox("How much sun will the plant have?", options, format_func=lambda x: display[x])

st.write("")
st.write("")

display = ("Click me, too",
          "Once a month (Little)",
          "Twice a month (Sometimes)",
           "Once a week (Often)",
            "Twice a week (Very often)")

options = list(range(len(display)))
value_water = st.selectbox("How often will you be able to water the plant?", options, format_func=lambda x: display[x])

st.write("")
st.write("")
st.write("")

st.markdown('**Please upload an image of your plant**')

# Image uploader, prediction, and data retrieval

uploaded_file = st.file_uploader('')

if uploaded_file is not None:
    # preprocess the image
    image = Image.open(uploaded_file)
    st.image(image, caption='Uploaded Image.', use_column_width=True)
    st.write("")
    pic = np.array(resizeimage.resize_cover(image, [150, 150]))
    X_list = []
    X_list.append(pic)
    X = np.stack(X_list, axis=0)
    X = preprocess_input(X)

    # load model and predict
    reconstructed_model = load_model('bulber_v2')
    y_pred_recon = reconstructed_model.predict(X)
    label_enc = load('label_encoder.joblib')
    columns = label_enc.classes_

    # return top species and transpose to have species as index column
    y_pred_recon_df = pd.DataFrame(y_pred_recon, columns = columns)
    output = y_pred_recon_df.idxmax(axis=1)[0]
    st.write(output)
    transpose = y_pred_recon_df.T

    pd.set_option('display.max_colwidth', -1)
    plant_info = plants_full_info_df[plants_full_info_df.Species.str.contains(output)]

    # Show prediction results
    st.subheader('**We think your species is...**')

    st.write(plant_info['Species'].to_string()[5:])


    st.write("")
    st.write("")

    st.subheader('**...but you might know it by:**')
    st.write(plant_info['Common names'].to_string()[5:])

    st.write("")
    st.write("")

    st.subheader(f"**Some information on {plant_info['Species'].iloc[0]}**")
    st.write(plant_info['Description'].to_string()[5:])

    st.write("")
    st.write("")
    st.write("")

    crawl_indexed = plants_full_info_df.set_index('Species')

    water_num = crawl_indexed.loc[plant_info['Species'].iloc[0]]['Water']
    light_num = crawl_indexed.loc[plant_info['Species'].iloc[0]]['Light']

    st.subheader('**Matching results...**')

    if value_water == water_num and value_light == light_num:
      st.write(f"**Congratulations! You have a match. {plant_info['Species'].iloc[0]} will be happy in the conditions you provided.**")
      st.balloons()
      st.write("")
      st.write("")
      st.subheader('Here are some additional details about how to look after your new plant!')
      st.write("")

      st.markdown('**Growing instructions**')
      st.write(plant_info['How to Grow'].iloc[0])
      st.write("")
      st.markdown('**Things to look out for**')
      st.write(plant_info['How to Care'].iloc[0])

    else:
      st.write(f"Bad news :(")
      st.write("")
      st.write(f"**{plant_info['Species'].iloc[0]} is not a good fit for the conditions you provided.**")

      merged = pd.merge(crawl_indexed, transpose, left_index=True, right_index=True)
      matching_ones = merged.loc[merged['Light']==value_light].loc[merged['Water']==value_water]


      full_merge = pd.merge(matching_ones, image_urls, left_index=True, right_index=True)
      full_merge['rounded_rank'] = round(full_merge.iloc[:,-2], 4)
      full_merge.reset_index(inplace=True)

      if full_merge.empty:
          st.write("Sorry but we do not have any species that meet your requirements at this stage")
      else:
          row = full_merge.sort_values(by='rounded_rank', ascending=False).iloc[0]['Species']
          row
          st.write("**But we might have one you will like and that would be very happy with you:**")
          st.write(f"The {row}")

          image_best = full_merge.sort_values(by='rounded_rank', ascending=False).iloc[0]['img_url_flowers']
          st.image(image_best, use_column_width=True)
