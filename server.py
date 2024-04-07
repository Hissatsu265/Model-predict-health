from flask import Flask, request, jsonify
import pandas as pd
from keras import models
from sklearn.preprocessing import StandardScaler
import tensorflow as tf
import numpy as np
from keras.models import load_model
# --------------------------------------------------------
app = Flask(__name__)

model = models.load_model("my_model_xray.h5")
model1 = models.load_model("my_model.h5")
model2 = load_model("my_model_xray_CV.h5")
@app.route('/')
def home():
    return "Welcome to the Heart Disease Prediction API!"

@app.route('/predict', methods=['POST'])
def predict():
    try:
        data = request.get_json()

        if len(data['features']) < 12:
            return jsonify({'error': 'Invalid input format'}), 400
        t = [int(value) for value in data['features']]
        print(t)
        type= [int(value) for value in data['type']]
# ----------------------------------------------------------------------------------------
        if(type[0]==2):
            raw_data = pd.read_csv(r"diabetes_data.csv")
            df = pd.DataFrame([{
                'Age': t[0], 'Sex': t[1], 'HighChol': t[2], 'BMI': t[3],
                'HeartDiseaseorAttack': t[4], 'PhysActivity': t[5],
                'Fruits': t[6], 'Veggies': t[7], 'GenHlth': t[8] + 1, 'PhysHlth': t[9], 'DiffWalk': t[10], 'HighBP': t[11],
                'Diabetes': 0
            }])

            raw_data = raw_data.drop(['CholCheck', 'Smoker', 'HvyAlcoholConsump', 'MentHlth', 'Stroke'], axis=1)
            raw_data = pd.concat([raw_data, df], ignore_index=True)

            columns_to_get_dummies = ['Sex', 'HighChol', 'HighBP', 'PhysActivity', 'Fruits', 'Veggies',
                                      'HeartDiseaseorAttack', 'DiffWalk']
            data = pd.get_dummies(raw_data, columns=columns_to_get_dummies)
            standardScaler = StandardScaler()
            columns_to_scale = ['Age', 'BMI', 'GenHlth', 'PhysHlth']

            data[columns_to_scale] = standardScaler.fit_transform(data[columns_to_scale])
            data = data.dropna()
            # print(data.info())
            # print(data.columns)
            bool_columns = ['Age', 'BMI', 'GenHlth', 'PhysHlth', 'Diabetes', 'Sex_0', 'Sex_1',
                            'HighChol_0', 'HighChol_1', 'HighBP_0', 'HighBP_1', 'PhysActivity_0',
                            'PhysActivity_1', 'Fruits_0', 'Fruits_1', 'Veggies_0', 'Veggies_1',
                            'HeartDiseaseorAttack_0', 'HeartDiseaseorAttack_1', 'DiffWalk_0',
                            'DiffWalk_1']
            data[bool_columns] = data[bool_columns].astype(int)
            X_test = data.drop('Diabetes', axis=1)
            X_test = X_test.iloc[[-1]]
            prediction = model.predict(X_test)
            print(int(float(prediction[0, 0]) * 10000))
            return jsonify({'prediction': int(float(prediction[0, 0]) * 10000)})
        else:
            # print(t)
            raw_data = pd.read_csv(r"data_heart.csv")
            df = pd.DataFrame([{
                'age': t[0],
                'sex': t[1],
                'cp': t[2],
                'trestbps': t[3],
                'chol': t[4],
                'fbs': t[5],
                'restecg': t[6],
                'thalach': t[7],
                'exang': t[8],
                'oldpeak': t[9] * 1.0,
                'slope': t[10],
                'ca': t[11],
                'thal': t[12],
                'target': 0
            }])
            raw_data = pd.concat([raw_data, df], ignore_index=True)

            columns_to_get_dummies = ['sex', 'cp', 'fbs', 'restecg', 'exang', 'slope', 'ca', 'thal']
            data = pd.get_dummies(raw_data, columns=columns_to_get_dummies)
            standardScaler = StandardScaler()
            columns_to_scale = ['age', 'trestbps', 'chol', 'thalach', 'oldpeak']
            data[columns_to_scale] = standardScaler.fit_transform(data[columns_to_scale])
            # print(data.info())
            bool_columns = ['sex_0.0', 'sex_1.0', 'cp_0', 'cp_1', 'cp_2', 'cp_3',
                            'fbs_0', 'fbs_1', 'restecg_0', 'restecg_1', 'restecg_2', 'exang_0',
                            'exang_1', 'slope_0', 'slope_1', 'slope_2', 'ca_0', 'ca_1', 'ca_2', 'ca_3',
                            'ca_4', 'thal_0', 'thal_1', 'thal_2', 'thal_3']

            data[bool_columns] = data[bool_columns].astype(int)
            X_test = data.drop('target', axis=1)
            X_test = X_test.iloc[[-1]]
            prediction = model1.predict(X_test)
            print(int(float(prediction[0, 0]) * 10000))
            return jsonify({'prediction': int(float(prediction[0, 0]) * 10000)})
    except Exception as e:
        print(str(e))
        return jsonify({'error': str(e)}), 500
def preprocess_image(image):
    image = tf.image.resize(image, (120, 120))
    image = np.array(image)
    image = image / 255.0
    return image

@app.route('/predict_xray', methods=['POST'])
def predict1():
    image_file = request.files['image']
    image = tf.image.decode_image(image_file.read(), channels=3)
    preprocessed_image = preprocess_image(image)
    preprocessed_image = np.expand_dims(preprocessed_image, axis=0)
    prediction = model2.predict(preprocessed_image)
    print(prediction[0][0])
    response = {'prediction': int(prediction[0][0]*10000)}
    return jsonify(response)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
