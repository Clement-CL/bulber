import streamlit as st
from PIL import Image
from bumbulb.data import get_data
from sklearn.preprocessing import LabelEncoder
import numpy as np
import pandas as pd
from tensorflow.keras.models import load_model
import time

# Page formatting and image display

crawl = pd.read_csv('bumbulb/df_new2.csv')
st.set_option('deprecation.showfileUploaderEncoding', False)
st.markdown("<h1 style='text-align: left; color: red;'img/h1>", unsafe_allow_html=True)
img = st.image('bumbulb/untitled.png', width=700, output_format='png')

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
value_water = st.selectbox("How many times do you want to water the plant?", options, format_func=lambda x: display[x])

st.write("")
st.write("")
st.write("")

st.markdown('**Please upload an image of your plant**')
# Image uploader, prediction, and data retrieval

uploaded_file = st.file_uploader('')
if uploaded_file is not None:
    image = Image.open(uploaded_file)
    st.image(image, caption='Uploaded Image.', use_column_width=True)
    st.write("")
    pic_in_iter = np.array(Image.open(uploaded_file))
    X_list = []
    X_list.append(pic_in_iter)
    X = np.stack(X_list, axis=0)

    reconstructed_model = load_model('bumbulb_VGG16_v2')
    y_pred_recon = reconstructed_model.predict(X)
    # label_enc = load('label_enc.joblib')
    # columns = label_enc.classes_
    columns = np.array(['Acanthus mollis', 'Carpobrotus edulis',
                   'Alisma plantago-aquatica', 'Begonia evansiana', 'Cistus albidus',
                   'Bryonia cretica', 'Arbutus unedo', 'Castanea sativa',
                   'Centaurium erythraea', 'Gunnera tinctoria', 'Deutzia scabra',
                   'Hypericum androsaemum', 'Crocosmia x crocosmiiflora',
                   'Lilium bulbiferum', 'Lagerstroemia indica',
                   'Magnolia grandiflora', 'Eucalyptus globulus', 'Nelumbo nucifera',
                   'Bougainvillea spectabilis', 'Nymphaea alba',
                   'Anacamptis pyramidalis', 'Antirrhinum majus',
                   'Argentina anserina', 'Brugmansia suaveolens',
                   'Athyrium filix-femina'])

    y_pred_recon_df = pd.DataFrame(y_pred_recon, columns = columns)
    output = y_pred_recon_df.idxmax(axis=1)[0]

    transpose = y_pred_recon_df.T
    transpose

    # st.write(type(output))
    # st.write(output)

    pd.set_option('display.max_colwidth', -1)
    info_needed = crawl[crawl.Species.str.contains(output, case=False)]

    # USER RESULTS
    st.subheader('**We think your species is...**')

    st.write(info_needed['Species'].to_string()[5:])

    st.write("")
    st.write("")

    st.subheader('**...but you might know it by:**')
    st.write(info_needed['Common names'].to_string()[5:])

    st.write("")
    st.write("")

    st.subheader(f"**Some information on {info_needed['Species'].iloc[0]}**")
    st.write(info_needed['Description'].to_string()[5:])

    st.write("")
    st.write("")
    st.write("")

    crawl_indexed = crawl.set_index('Species')

    water_num = crawl_indexed.loc[info_needed['Species'].iloc[0]]['Water']
    light_num = crawl_indexed.loc[info_needed['Species'].iloc[0]]['Light']

    st.subheader('**Your results...**')
    if value_water == water_num and value_light == light_num:
      st.write(f"**Congratulations! You have a match. {info_needed['Species'].iloc[0]} will be happy in the conditions you provided.**")
      st.balloons()
      st.write("")
      st.write("")
      st.subheader('Here are some additional details about how to look after your new plant!')
      st.write("")

      st.markdown('**Growing instructions**')
      st.write(info_needed['How to Grow'].iloc[0])
      st.write("")
      st.markdown('**Things to look out for**')
      st.write(info_needed['How to Care'].iloc[0])

    else:
      st.write(f"Bad news :(")
      st.write("")
      st.write(f"**{info_needed['Species'].iloc[0]} is not a good fit for the conditions you provided.**")
      #st.image('https://bs.floristic.org/image/o/cbe32b44e6a411ebb28153d43afad1a4f78a4ee9', width=400)
      y_pred_recon_df['match'] = value_water == water_num and value_light == light_num

      merged = pd.merge(crawl_indexed, transpose, left_index=True, right_index=True)

      matching_ones = merged.loc[merged['Light']==value_light].loc[merged['Water']==value_water]
      # transpose

      image_urls = pd.read_csv('bumbulb/links_to_images.csv').set_index('Species')

      full_merge = pd.merge(matching_ones, image_urls, left_index=True, right_index=True)

      full_merge['rounded_rank'] = round(full_merge.iloc[:,-2], 4)
      # st.write(full_merge.iloc['Argentina anserina'])
      # st.write(full_merge.iloc[:,-1].max())
      # test= full_merge.loc[full_merge['rounded_rank'].max()]
      # st.write(test)
      full_merge.reset_index(inplace=True)
      row = full_merge.sort_values(by='rounded_rank', ascending=False).iloc[0]['index']

      st.write(row)

      image_best = full_merge.sort_values(by='rounded_rank', ascending=False).iloc[0]['image_urls']
      st.image(image_best)
      # st.write(full_merge.index.get_slice_bound(full_merge.loc[full_merge['rounded_rank'].max()], side='left', kind='loc'))
      # st.write(test)

      #st.write(f"We think {full_merge.loc[full_merge.iloc[:,-2].max()]['Species']} would be a good fit, though.")

      # matching_ones.loc[matching_ones['']]
    # st.write("")
    # st.write("")
