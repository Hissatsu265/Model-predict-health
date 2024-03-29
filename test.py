from flask import Flask, request, jsonify
from sklearn.preprocessing import StandardScaler
import joblib
import pandas as pd


model = joblib.load("model_svm_healthprediction.joblib")

raw_data = pd.read_csv(r"dataset.csv")
df = pd.DataFrame([{
    'age': 22,
    'sex': 1,
    'nature_of_work':0,
    'time_work':30,
    'health_care':0,
    'pathology':1,
    'work_env':1,
    'BMI':24.8,
    'target': 0
}])
raw_data = pd.concat([raw_data, df], ignore_index=True)

columns_to_get_dummies = ['sex', 'nature_of_work', 'health_care', 'pathology', 'work_env']
data = pd.get_dummies(raw_data, columns=columns_to_get_dummies)
standardScaler = StandardScaler()
columns_to_scale = ['age', 'time_work','BMI']
data[columns_to_scale] = standardScaler.fit_transform(data[columns_to_scale])
# print(data.info())


bool_columns=['sex_0','sex_1','nature_of_work_0','nature_of_work_1',
'nature_of_work_2','health_care_0','health_care_1','health_care_2',
'health_care_3','pathology_0','pathology_1','pathology_2','work_env_0',
'work_env_1','work_env_2','work_env_3']

data[bool_columns] = data[bool_columns].astype(int)
X_test = data.drop('target', axis=1)
X_test = X_test.iloc[[-1]]
prediction = int(model.predict(X_test)[0])

# print(prediction)