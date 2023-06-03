import os
import matplotlib.pyplot as plt

from analyzers.pipeline.stage import PipelineStage
import json

class CIPlotter(PipelineStage):
    def __init__(self):
        pass

    def run(self):
        # Load your JSON data
        with open('./new_output/ci_analysis.json') as f:
            data = json.load(f)

        with open('./new_output/overall_stats.json') as f:
            overall_stats = json.load(f)

        # Extract repo-workflow names, success rates and average execution times
        repo_workflows = list(data.keys())
        success_rates = [value['success_rate'] for value in data.values()]
        avg_execution_times = [value['average_execution_time'] for value in data.values()]

        # Create a new directory if it doesn't exist
        if not os.path.exists('new_output/plots'):
            os.makedirs('new_output/plots')

        # Plot success rates
        plt.figure(figsize=(15,10))
        # can we have 2 decimal floats for the bar plot
        plt.barh(repo_workflows, success_rates)
        plt.xlabel('Success Rate')
        plt.ylabel('Repository-Workflow')
        plt.title('Success Rates for each Repository-Workflow')
        plt.xticks(list(plt.xticks()[0]) + [overall_stats['median_success_rate']])
        plt.xticks(list(plt.xticks()[0]) + [overall_stats['average_success_rate']])
        # plot median success rate
        plt.axvline(x=overall_stats['median_success_rate'], color='green', label='Median Success Rate')
        plt.axvline(x=overall_stats['average_success_rate'], color='red', label='Average Success Rate')
        plt.tight_layout()  # Ensure labels are not cut off
        plt.savefig('new_output/plots/success_rates.png')
        plt.close()

        # Plot average execution times
        plt.figure(figsize=(15,10))
        plt.barh(repo_workflows, avg_execution_times)
        plt.xlabel('Average Execution Time (s)')
        plt.ylabel('Repository-Workflow')
        # lets plot the average execution time
        plt.axvline(x=overall_stats['median_execution_time'], color='green', label='Median Execution Time')
        plt.axvline(x=overall_stats['average_execution_time'], color='red', label='Average Execution Time')
        # lets add a extra point on the x axis for the value of the average execution time
        plt.xticks(list(plt.xticks()[0]) + [overall_stats['median_execution_time']])
        plt.xticks(list(plt.xticks()[0]) + [overall_stats['average_execution_time']])
        plt.title('Average Execution Times for each Repository-Workflow')
        plt.tight_layout()  # Ensure labels are not cut off
        plt.savefig('new_output/plots/avg_execution_times.png')
        plt.close()
