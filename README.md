# What is bulber

bulber is an app that uses a neural network to match users with a plant they like and that would like them back.

# Why bulber

While flower markets are growing rapidly in the UK, the choice for the right plant remains a hassle when living in a flat with limited outdoor space and/or sun exposure.
bulber will give you all the information you need to know if you are a match and if you’re not, it will introduce you to its nearest neighbors for a long lasting pairing

# Where did we source the data

Query the Trefle and Wikipedia API
- The Wiki API provided plants characteristics
- The Trefle API provided plants requirements (light, water, care and grow instructions)

Scraping PlantNet site
- The site contains 7,554 species and 3,361,926 photos Western Europe only on the same page

# Models used

Baseline 1: Random classification
- 4% success rate (top probability is the correct species)

Baseline 2: Convolutional neural network with three convolutional layers separated by three pooling layers and followed by a Flattening and a Dense layer.
- 44% success rate (top probability is the correct species)

Model 3: Transfer Learning with VGG16 from "Very Deep Convolutional Networks for Large-Scale Image Recognition”
- The model also uses convolutional & max pooling layers but uses 16 and was trained on +14M images.
- 60% success rate (top probability is the correct species)

# Data pre-processing (outside of VGG16 preprocessing from tensorflow.keras)

Review of our baseline model showed underperformance was correlated with number of images available.
- I.e Species with low numbers of images yielded poor model performance
- We also saw varied results between the types of images (flowers vs leaf images depending on the species)

Test 1 - Undersampling: Train the model with balanced dataset by dropping images from the most represented spiecies
- 48% success rate (top probability is the correct species)
Test 2 - Oversampling: using Keras.ImageDataGenerator to increase the number of images for less represented species.
- 60% success rate (top probability is the correct species)

# Predictions and recommendation in Streamlit app

Step 1: The user select the care he/she can provide to the plant
Step 2: The user inputs an image of a plant he likes
Step 3: The model matches the plant with a species and review the care requirements with the ones entered in step 1.

Result:
if it's a match the user is provided with more information on the plant
if it is not a match we use the predictions of the model to find the nearest looking plant that meets the user's criteria.
