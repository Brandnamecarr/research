import pandas as pd
import numpy as np

from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split

# Regression models
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LinearRegression, Ridge, Lasso, ElasticNet


housing_df = pd.read_csv('../Data/CSVs/Housing.csv')

# print(housing_df.columns)
print(housing_df.info())

# print(housing_df.head())

# split into x and y
x = housing_df[['area', 'bedrooms', 'stories', 'bathrooms', 'parking']]
y = housing_df['price']

# split to data into training and testing
xtrain, xtest, ytrain, ytest = train_test_split(x, y, test_size=0.2)

# instantiate and fit the model
model = RandomForestRegressor()
model.fit(xtrain, ytrain)
score = model.score(xtest, ytest)
print(f"RandomForestRegressor() => {score}")
