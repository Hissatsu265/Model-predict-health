from flask import Flask, request, jsonify
from sklearn.preprocessing import StandardScaler
import joblib
import pandas as pd
# //-------------------------------------------------------
import tensorflow as tf
from keras import models
from keras import layers
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import classification_report
# --------------------------------------------------------
app = Flask(__name__)

model = models.load_model("my_model_xray.h5")
# model = joblib.load("my_model.h5")
@app.route('/')
def home():
    return "Welcome to the Heart Disease Prediction API!"

@app.route('/predict', methods=['POST'])
def predict():

    try:
        data = request.get_json()

        if len(data['features']) != 12:
            return jsonify({'error': 'Invalid input format'}), 400
        t = [int(value) for value in data['features']]
        print(t)
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
        print(data.info())
        # print(data.columns)
        bool_columns = ['Age', 'BMI', 'GenHlth', 'PhysHlth', 'Diabetes', 'Sex_0', 'Sex_1',
                        'HighChol_0', 'HighChol_1', 'HighBP_0', 'HighBP_1', 'PhysActivity_0',
                        'PhysActivity_1', 'Fruits_0', 'Fruits_1', 'Veggies_0', 'Veggies_1',
                        'HeartDiseaseorAttack_0', 'HeartDiseaseorAttack_1', 'DiffWalk_0',
                        'DiffWalk_1']

        # data[bool_columns] = data[bool_columns].astype(int)
        # X_test = data.drop('Diabetes', axis=1)
        # X_test = X_test.iloc[[-1]]
        #
        # prediction = model.predict(X_test)
        # print(int(float(prediction[0,0])*10000))
        # return jsonify({'prediction': int(float(prediction[0,0])*10000)})

        data[bool_columns] = data[bool_columns].astype(int)
        X_test = data.drop('Diabetes', axis=1)
        X_test = X_test.iloc[[-1]]
        prediction = model.predict(X_test)
        print(int(float(prediction[0, 0]) * 10000))
        return jsonify({'prediction': int(float(prediction[0, 0]) * 10000)})

    except Exception as e:
        print(str(e))
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
