
from keras import models
import tensorflow as tf
from flask import Flask, request, jsonify
import pandas as pd
from keras import models
from sklearn.preprocessing import StandardScaler
# --------------------------------------------------------
model = models.load_model("my_model_xray_CV.h5")

test_dir = 'D:\hk6\Model\Test_xray'


test_data = tf.keras.utils.image_dataset_from_directory(
    test_dir,
    labels='inferred',
    label_mode='binary',
    image_size=(120, 120),
    batch_size=1,
    shuffle=False,
    seed=42,
    validation_split=None,
    subset=None
)

for images, labels in test_data.take(2):  # Lấy 1 batch
    predictions = model.predict(images)
    for j in range(min(len(images), 1)):
        probability = predictions[j] * 100.0
        print('The probability of Pneumonia is: ', predictions[j]*100)
