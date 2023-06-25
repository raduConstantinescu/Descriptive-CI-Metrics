import json
import numpy as np
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, confusion_matrix, precision_score, recall_score, f1_score
from sklearn.utils import class_weight

from project_maturity_v2.utils import extract_data_from_json


class LogisticRegressionAnalyzer():
    def __init__(self):
        self.metrics_data = extract_data_from_json('../outputs_v2/repo_data.json')
        self.labels_data = extract_data_from_json('../outputs_v2/repo_maturity.json')

    def analyze(self):
        # Step 2: Preprocess the data
        metrics_list = []
        labels_list = []

        # Specify the metrics you want to include
        selected_metrics = ['stargazers_count','forks_count', 'contributors_count']

        for repo_name, metrics in self.metrics_data.items():
            if repo_name not in self.labels_data.keys():
                continue
            selected_metrics_values = [metrics[metric] for metric in selected_metrics]
            metrics_list.append(selected_metrics_values)
            labels_list.append(self.labels_data[repo_name])

        X = np.array(metrics_list)
        y = np.array(labels_list)

        # Step 3: Split the data into training and testing sets
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

        # Step 4: Train the logistic regression model with class weight adjustment
        class_weights = class_weight.compute_class_weight(class_weight='balanced', classes=np.unique(y_train), y=y_train)
        logreg = LogisticRegression(class_weight=dict(enumerate(class_weights)))
        logreg.fit(X_train, y_train)

        # Step 5: Predict labels for the test data
        y_pred = logreg.predict(X_test)

        # Step 6: Calculate evaluation metrics
        accuracy, cm, precision, recall, f1 = self.calculate_metrics(y_test, y_pred)

        print("Accuracy:", accuracy)
        print("Confusion Matrix:\n", cm)
        print("Precision:", precision)
        print("Recall:", recall)
        print("F1-score:", f1)

        # Step 7: Perform cross-validation
        cv_scores = cross_val_score(logreg, X, y, cv=5)
        print("Cross-Validation Scores:", cv_scores)
        print("Average Cross-Validation Accuracy:", np.mean(cv_scores))

    # Function to calculate evaluation metrics
    def calculate_metrics(self, y_true, y_pred):
        accuracy = accuracy_score(y_true, y_pred)
        cm = confusion_matrix(y_true, y_pred)
        precision = precision_score(y_true, y_pred)
        recall = recall_score(y_true, y_pred)
        f1 = f1_score(y_true, y_pred)

        return accuracy, cm, precision, recall, f1

LogisticRegressionAnalyzer().analyze()