from datetime import datetime

from dateutil.relativedelta import relativedelta
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn import metrics as mtr

from build_performance.stage.stage import PipelineStage
from build_performance.utils import load_json_data
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression

class RepoProjectLevelMetricsLogisticRegression(PipelineStage):
    def __init__(self):
        pass

    def run(self):
        data = load_json_data('./output/stats/build_performance_with_main_branch_runs.json')

        workflows = []
        for repoName, repoData in data.items():
            for workflowName, workflowData in repoData.items():
                workflow = {}
                workflow['repo'] = repoName
                workflow['workflow'] = workflowName
                workflow['quadrant'] = workflowData['quadrant']
                metrics = workflowData['metrics']

                # Process the 'created_at' field
                created_at = workflowData['metrics']['created_at']
                created_at_datetime = datetime.strptime(created_at, '%Y-%m-%dT%H:%M:%S')
                current_datetime = datetime.now()
                rd = relativedelta(current_datetime, created_at_datetime)
                project_age_in_months = rd.years * 12 + rd.months
                del metrics['created_at']
                metrics['age'] = project_age_in_months

                workflow['metrics'] = metrics
                workflows.append(workflow)

        print(workflows[0])

        df = pd.DataFrame(workflows)

        # Convert the dictionaries in 'metrics' to separate columns
        df = pd.concat([df.drop(['metrics'], axis=1), df['metrics'].apply(pd.Series)], axis=1)

        # Drop the 'main_branch' column
        df = df.drop(columns=['main_branch'])
        df = df.drop(columns=['age'])
        encoder = LabelEncoder()

        # Fit the encoder and transform the 'language' column
        df['language'] = encoder.fit_transform(df['language'])

        X = df.drop(columns=['quadrant', 'repo', 'workflow'])
        y = df['quadrant']

        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)


        model = LogisticRegression(max_iter=1000)
        model.fit(X_train_scaled, y_train)
        y_pred = model.predict(X_test_scaled)

        accuracy = mtr.accuracy_score(y_test, y_pred)
        print(f"Model accuracy: {accuracy}")



