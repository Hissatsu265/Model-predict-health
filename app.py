from flask import Flask, request, jsonify
from sklearn.preprocessing import StandardScaler
import joblib
import pandas as pd
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Dropout
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import classification_report
app = Flask(__name__)

model = joblib.load("model_svm_heartdeases.joblib")
@app.route('/')
def home():
    return "Welcome to the Heart Disease Prediction API!"

@app.route('/predict', methods=['POST'])
def predict():
    try:
        data = request.get_json()

        if len(data['features']) != 13:
            return jsonify({'error': 'Invalid input format'}), 400
        t = [int(value) for value in data['features']]
        # print(t)
        raw_data = pd.read_csv(r"heart.csv")
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
        bool_columns=['sex_0', 'sex_1', 'cp_0', 'cp_1', 'cp_2', 'cp_3',
                      'fbs_0', 'fbs_1', 'restecg_0', 'restecg_1', 'restecg_2', 'exang_0',
                      'exang_1', 'slope_0', 'slope_1', 'slope_2', 'ca_0', 'ca_1', 'ca_2', 'ca_3',
                      'ca_4', 'thal_0', 'thal_1', 'thal_2', 'thal_3']

        data[bool_columns] = data[bool_columns].astype(int)
        X_test = data.drop('target', axis=1)
        X_test = X_test.iloc[[-1]]
        # print(X_test.info())
        prediction = int(model.predict(X_test)[0])

        return jsonify({'prediction': prediction})

    except Exception as e:
        print(str(e))
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
