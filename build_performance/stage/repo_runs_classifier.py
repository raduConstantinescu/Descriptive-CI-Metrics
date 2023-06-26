import pandas as pd
from matplotlib import pyplot as plt
import seaborn as sns


from build_performance.stage.stage import PipelineStage
from build_performance.utils import load_json_data

'''
We will classify again workflows based on which quadrant they belong to
we will look in each quadrant, for a workflow what is the run_performance of the workflow,
the run performance has keys the run attempts and the values are the breakage rate
we will take the average of the breakage rates and we will classify the workflow in the quadrant
'''

class RepoRunsClassifier(PipelineStage):
    def __init__(self):
        pass

    def run(self):
        print("RepoRunsClassifier")
        build_performance_data = load_json_data('./output/stats/build_performance_with_main_branch_runs.json')
        quadrant_workflows_by_run_perf = {}

        for repoName, workflows in build_performance_data.items():
            for workflowName, workflowData in workflows.items():
                quadrant = workflowData['quadrant']
                if quadrant not in quadrant_workflows_by_run_perf:
                    quadrant_workflows_by_run_perf[quadrant] = {}
                run_perf = workflowData['run_performance']
                for key, value in run_perf.items():
                    # looking at 1, 2 3+ keys
                    key = str(key) if int(key) <=3 else '>3'
                    if key not in quadrant_workflows_by_run_perf[quadrant]:
                        quadrant_workflows_by_run_perf[quadrant][key] = {
                            'breakage_rates': [],
                        }
                    quadrant_workflows_by_run_perf[quadrant][key]['breakage_rates'].append(value['breakage_rate'])

        for quadrant, run_perf in quadrant_workflows_by_run_perf.items():
            for run_attempt, data in run_perf.items():
                data['average_breakage_rate'] = 0
                if len(data['breakage_rates']) > 0:
                    data['average_breakage_rate'] = sum(data['breakage_rates']) / len(data['breakage_rates'])
                # drop breakage rates
                data['sample_size'] = len(data['breakage_rates'])
                data.pop('breakage_rates', None)

        print(quadrant_workflows_by_run_perf)
        df = self.create_table(quadrant_workflows_by_run_perf)
        self.visualize_data(df)
        print(df.to_latex(index=False))

    def create_table(self, data):
        table_data = []

        for quadrant, run_perf in data.items():
            run_perf_sorted = {k: run_perf[k] for k in sorted(run_perf, key=lambda x: float('inf') if x == '3+' else int(x))}
            for run_attempt, data in run_perf_sorted.items():
                table_data.append([quadrant, run_attempt, data['average_breakage_rate'], data['sample_size']])

        df = pd.DataFrame(table_data,
                          columns=['Quadrant', 'Run Attempt', 'Average Breakage Rate', 'Sample Size'])

        df['Average Breakage Rate'] = df['Average Breakage Rate'].map("{:.2f}%".format)

        return df

    def create_table(self, data):
        table_data = []

        for quadrant, run_perf in data.items():
            for run_attempt, data in run_perf.items():
                table_data.append([quadrant, run_attempt, data['average_breakage_rate'], data['sample_size']])

        df = pd.DataFrame(table_data,
                          columns=['Quadrant', 'Run Attempt', 'Average Breakage Rate', 'Sample Size'])

        df['Average Breakage Rate'] = df['Average Breakage Rate'].map("{:.2f}%".format)

        # Define the quadrant order and rename time to duration
        quadrant_order = ['LBLT', 'LBHT', 'HBLT', 'HBHT']
        quadrant_names = ['LBLD', 'LBHD', 'HBLD', 'HBHD']

        df['Quadrant'] = pd.Categorical(df['Quadrant'], categories=quadrant_order, ordered=True)

        df.sort_values(by='Quadrant', inplace=True)

        df['Quadrant'] = df['Quadrant'].replace(quadrant_order, quadrant_names)

        return df

    def visualize_data(self, df):
        df['Average Breakage Rate'] = df['Average Breakage Rate'].str.rstrip('%').astype('float')
        plt.figure(figsize=(10, 6))

        sns.barplot(x='Quadrant', y='Average Breakage Rate', hue='Run Attempt', data=df, palette='viridis')
        plt.grid(axis='y')

        plt.title('Average Breakage Rate by Quadrant and Run Attempt', fontsize=16)
        plt.xlabel(' Performance Quadrant', fontsize=14)
        plt.ylabel('Average Breakage Rate', fontsize=14)
        plt.ylim(0, df['Average Breakage Rate'].max() + 0.1)  # set y limit

        plt.savefig('./output/plots/run_attempt_performance.png')
        plt.show()

