# TABLE OF CONTENTS OF INFORMATION
what_were_covering = [
    "0. An end-to-end Scikit-learn workflow",
    "1. Getting the data ready",
    "2. Choose the right estimator/algorithm for our problems",
    "3. Fit the model/algorithm and use it to make predictions in our data",
    "4. Evaluating the model",
    "5. Improving the model",
    "6. Save and load a trained model",
    "7. Putting it all together!"
]

# SPECIFICALLY COVERING 1: ENCODING NON-NUMERICAL DATA

############# IMPORTS #################

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


from sklearn.metrics import classification_report, confusion_matrix, accuracy_score

from sklearn.model_selection import train_test_split

# turn categorical data into numbers
from sklearn.preprocessing import OneHotEncoder
from sklearn.compose import ColumnTransformer

from sklearn.ensemble import RandomForestRegressor

# read in csv with numerical and string data
car_sales = pd.read_csv("../Data/CSVs/car-sales-extended.csv")

# split into x, y
x = car_sales.drop('Price', axis=1)
y = car_sales['Price']

# have to convert string data to numbers.
# can also handle NaN/None/NULL values. 
categorical_features = ["Make", "Colour", "Doors"]
one_hot = OneHotEncoder()
transformer = ColumnTransformer([("one_hot", one_hot, categorical_features)], remainder="passthrough")

transformed_x = transformer.fit_transform(x)
# print(transformed_x)

# split into training and test set
xtrain, xtest, ytrain, ytest = train_test_split(transformed_x, y, test_size=0.2)

# build model
model = RandomForestRegressor()
model.fit(xtrain, ytrain)
score = model.score(xtest, ytest)
#print(f"Score: {score}")


