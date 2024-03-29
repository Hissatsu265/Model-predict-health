from flask import Flask, request, jsonify,render_template

from sklearn.preprocessing import StandardScaler
import joblib
import pandas as pd

app = Flask(__name__)
model = joblib.load("model_svm_healthprediction.joblib")

@app.route('/')
def home():
    return render_template('page.html')


@app.route('/predict', methods=['POST'])
def predict():
    try:
        data = request.get_json()
        if len(data['features']) != 8:
            return jsonify({'error': 'Invalid input format'}), 400
        t = [int(value) for value in data['features']]

        raw_data = pd.read_csv(r"dataset.csv")
        df = pd.DataFrame([{
            'age': t[0],
            'sex': t[1],
            'nature_of_work':t[2],
            'time_work':t[3],
            'health_care':t[4],
            'pathology':t[5],
            'work_env':t[6],
            'BMI':t[7]*1.,
            'target': 0
        }])
        raw_data = pd.concat([raw_data, df], ignore_index=True)

        columns_to_get_dummies = ['sex', 'nature_of_work', 'health_care', 'pathology', 'work_env']
        data = pd.get_dummies(raw_data, columns=columns_to_get_dummies)
        standardScaler = StandardScaler()
        columns_to_scale = ['age', 'time_work', 'BMI']
        data[columns_to_scale] = standardScaler.fit_transform(data[columns_to_scale])
        # print(data.info())

        bool_columns = ['sex_0', 'sex_1', 'nature_of_work_0', 'nature_of_work_1',
                        'nature_of_work_2', 'health_care_0', 'health_care_1', 'health_care_2',
                        'health_care_3', 'pathology_0', 'pathology_1', 'pathology_2', 'work_env_0',
                        'work_env_1', 'work_env_2', 'work_env_3']

        data[bool_columns] = data[bool_columns].astype(int)
        X_test = data.drop('target', axis=1)
        X_test = X_test.iloc[[-1]]
        prediction = int(model.predict(X_test)[0])

        return jsonify({'prediction': prediction})

    except Exception as e:
        print(str(e))
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
