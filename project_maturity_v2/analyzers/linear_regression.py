import json
from datetime import datetime
import statsmodels.api as sm

import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error

from project_maturity_v2.utils import extract_data_from_json


class LinearRegressionAnalyzer():
    def __init__(self):
        self.data = extract_data_from_json('../outputs_v2/repo_data.json')
        self.maturity_info = extract_data_from_json('../outputs_v2/repo_maturity.json')


    def analyze(self):

        df = pd.DataFrame(self.process_repo_data())
        # Create a pandas DataFrame from the JSON data
        # df = pd.DataFrame(self.data)

        df['maturity'] = df['repo_name'].map(self.maturity_info)
        df['maturity'] = df['maturity'].map({False: 0, True: 1})

        # Define the independent variables (metrics) and the dependent variable (maturity)
        metrics = ['forks_count', 'stargazers_count', 'contributors_count']
        dependent_variable = 'maturity'  # Assuming you have a column in your data indicating the maturity (e.g., "mature" or "immature")

        # Select the columns for the regression analysis
        df = df[metrics + [dependent_variable]]

        # Preprocess the data if necessary (e.g., convert timestamps, encode categorical variables)

        # Split the data into training and testing sets
        X_train, X_test, y_train, y_test = train_test_split(df[metrics], df[dependent_variable], test_size=0.2, random_state=42)
        null_indices = y_train[y_train.isnull()].index
        X_train = X_train.drop(null_indices)
        y_train = y_train.drop(null_indices)
        # Create a linear regression model
        model = LinearRegression()

        # Fit the model to the training data
        model.fit(X_train, y_train)

        # Make predictions on the testing data
        y_pred = model.predict(X_test)

        # Evaluate the model using mean squared error
        mse = mean_squared_error(y_test, y_pred)
        print("Mean Squared Error:", mse)

        # Print the coefficients and intercept
        print("Coefficients:", model.coef_)
        print("Intercept:", model.intercept_)

        # Add a constant term to the independent variables
        X_train = sm.add_constant(X_train)

        # Create and fit the linear regression model using statsmodels
        model = sm.OLS(y_train, X_train)
        results = model.fit()

        # Get the p-values for the coefficients
        p_values = results.pvalues

        print("P-values:", p_values)

        # print(results.summary().as_latex())

    def process_repo_data(self):
        # Create an empty list to store the dictionaries
        repo_data = []

        # Iterate over the JSON data and extract the repository information
        for repo_name, repo_info in self.data.items():
            repo_info['repo_name'] = repo_name
            repo_data.append(repo_info)

        return repo_data

LinearRegressionAnalyzer().analyze()