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

# SPECIFICALLY COVERING 1: sorting the data into labels and features.

############# IMPORTS #################

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


from sklearn.metrics import classification_report, confusion_matrix, accuracy_score

from sklearn.model_selection import train_test_split

## getting our data ready to be used for machine learning

## three main things to do:
# 1. Split data into features and labels (usually x and y).
# 2. Filling (also called imputing or disregarding) missing values.
# 3. Converting non-numerical values to numerical values (feature encoding).

heart_disease = pd.read_csv('../Data/CSVs/Data/CSVs/heart-disease.csv')
x = heart_disease.drop('target', axis=1) # axis=1 means COLUMNS
y = heart_disease['target']

# split the data into training and tests sets
x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.2)

print(f"{x_test.shape}, {x_test.shape}, {y_train.shape}, {y_test.shape}")


# BUT, WHAT ABOUT DATA THAT IS NON-NUMERICAL?
