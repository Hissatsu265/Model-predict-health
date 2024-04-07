from flask import Flask, request, jsonify
from keras.models import load_model
import tensorflow as tf
import numpy as np

app = Flask(__name__)

model = load_model("my_model_xray_CV.h5")
@app.route('/')
def home():
    return "Welcome to the Heart Disease Prediction API!"
def preprocess_image(image):
    image = tf.image.resize(image, (120, 120))
    image = np.array(image)
    image = image / 255.0
    return image

@app.route('/predict_xray', methods=['POST'])
def predict():
    image_file = request.files['image']
    image = tf.image.decode_image(image_file.read(), channels=3)
    preprocessed_image = preprocess_image(image)
    preprocessed_image = np.expand_dims(preprocessed_image, axis=0)
    prediction = model.predict(preprocessed_image)
    print(prediction[0][0])
    response = {'prediction': int(prediction[0][0]*10000)}
    return jsonify(response)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)