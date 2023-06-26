from build_performance.stage.stage import PipelineStage
from build_performance.utils import load_json_data, output_json_data
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np


class RepoTODAnalysis(PipelineStage):
    def __init__(self):
        pass

    def run(self):
        print("RepoTODAnalysis")
        build_performance_data = load_json_data('./output/stats/build_performance_with_metrics.json')
        quadrant_workflows_by_time_of_day = {}

        for repoName, workflows in build_performance_data.items():
            for workflowName, workflowData in workflows.items():
                quadrant = workflowData['quadrant']
                if workflowData['quarter_data'] is True:
                    continue
                if quadrant not in quadrant_workflows_by_time_of_day:
                    quadrant_workflows_by_time_of_day[quadrant] = {
                        'weekdays': {
                            'total': 0,
                            'failures': 0,
                        },
                        'weekend': {
                            'total': 0,
                            'failures': 0,
                        }
                    }

                days_of_week = workflowData['days_of_week']
                for day, data in days_of_week.items():
                    if day in ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']:
                        quadrant_workflows_by_time_of_day[quadrant]['weekdays']['total'] += data['total']
                        quadrant_workflows_by_time_of_day[quadrant]['weekdays']['failures'] += data['failures']
                    else:
                        quadrant_workflows_by_time_of_day[quadrant]['weekend']['total'] += data['total']
                        quadrant_workflows_by_time_of_day[quadrant]['weekend']['failures'] += data['failures']

        for quadrant, quadrant_data in quadrant_workflows_by_time_of_day.items():
            for label, label_data in quadrant_data.items():
                total = label_data['total']
                failures = label_data['failures']
                failure_rate = failures / total
                quadrant_workflows_by_time_of_day[quadrant][label]['failure_rate'] = failure_rate

        output_json_data('./output/stats/quadrant_workflows_by_time_of_day.json', quadrant_workflows_by_time_of_day)
        self.plot_data(quadrant_workflows_by_time_of_day)
        df = self.create_table(quadrant_workflows_by_time_of_day)
        # lets do df to latex
        print(df.to_latex(index=False))
        print(df)

    def plot_data(self, data):
        labels = ['weekdays', 'weekend']

        x = np.arange(len(labels))  # the label locations
        width = 0.2  # the width of the bars

        for quadrant, quadrant_data in data.items():
            total_values = [quadrant_data[label]['total'] for label in labels]
            failure_values = [quadrant_data[label]['failures'] for label in labels]
            failure_rate_values = [quadrant_data[label]['failure_rate'] for label in labels]

            fig, axs = plt.subplots(2)

            # First subplot for total and failures
            rects1 = axs[0].bar(x - width, total_values, width, label='Total')
            rects2 = axs[0].bar(x, failure_values, width, label='Failures')

            axs[0].set_ylabel('Count')
            axs[0].set_title('Builds and Failures for Quadrant ' + quadrant)
            axs[0].set_xticks(x)
            axs[0].set_xticklabels(labels)
            axs[0].legend()

            axs[0].bar_label(rects1, padding=3)
            axs[0].bar_label(rects2, padding=3)

            # Second subplot for failure rate
            rects3 = axs[1].bar(x, failure_rate_values, width, label='Failure Rate', color='r')

            axs[1].set_ylabel('Failure Rate')
            axs[1].set_title('Failure Rate for Quadrant ' + quadrant)
            axs[1].set_xticks(x)
            axs[1].set_xticklabels(labels)
            axs[1].legend()

            axs[1].bar_label(rects3, padding=3)

            fig.tight_layout()

        plt.show()

    def create_table(self, data):
        table_data = []

        for quadrant, quadrant_data in data.items():
            for label in ['weekdays', 'weekend']:
                total = quadrant_data[label]['total']
                failures = quadrant_data[label]['failures']
                failure_rate = quadrant_data[label]['failure_rate']

                table_data.append([quadrant, label, total, failures, failure_rate])

        df = pd.DataFrame(table_data, columns=['Quadrant', 'Day Type', 'Total', 'Failures', 'Failure Rate'])

        return df




