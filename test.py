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
model = models.load_model("my_model.h5")
t = [50,	1,	0,	140,	217,	0,	1,	111,	1,	5.6,	0,	0,	3
]
# print(type(t))

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
bool_columns=['sex_0.0', 'sex_1.0', 'cp_0', 'cp_1', 'cp_2', 'cp_3',
              'fbs_0', 'fbs_1', 'restecg_0', 'restecg_1', 'restecg_2', 'exang_0',
              'exang_1', 'slope_0', 'slope_1', 'slope_2', 'ca_0', 'ca_1', 'ca_2', 'ca_3',
              'ca_4', 'thal_0', 'thal_1', 'thal_2', 'thal_3']

data[bool_columns] = data[bool_columns].astype(int)
X_test = data.drop('target', axis=1)
X_test = X_test.iloc[[-1]]
print(X_test.shape)
prediction =model.predict(X_test)
print(prediction.shape)
print(prediction)
print(float(model.predict(X_test)[0,0])*100)
