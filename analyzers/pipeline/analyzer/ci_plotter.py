import os
import matplotlib.pyplot as plt

from analyzers.pipeline.stage import PipelineStage
import json

class CIPlotterConfig:
    def __init__(self, config):
        self.input_file = config["input_file"]
        self.stats_file = config["data_input_file"]
        self.output_dir = config["output_dir"]

class CIPlotter(PipelineStage):
    def __init__(self, args, config):
        self.args = args
        self.config = config
        self.exclude_workflows = ['microsoft/playwright-tests-551665', 'ytdl-org/youtube-dl-CI-4378722']

    def run(self):
        # Load your JSON data
        with open(self.config.input_file) as f:
            data = json.load(f)

        with open(self.config.stats_file) as f:
            overall_stats = json.load(f)

        # Filter out excluded workflows
        data = {k: v for k, v in data.items() if k not in self.exclude_workflows}

        # Extract repo-workflow names, success rates and average execution times
        repo_workflows = list(data.keys())
        repo_workflows = [repo.replace('\u2705', '').replace('\U0001F9EA', '').replace('\U0001F454', '') for repo in
                          repo_workflows]

        success_rates = [value['success_rate'] for value in data.values()]
        avg_execution_times = [value['average_execution_time'] for value in data.values()]

        # Create a new directory if it doesn't exist
        if not os.path.exists(self.config.output_dir):
            os.makedirs(self.config.output_dir)

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
        plt.savefig(os.path.join(self.config.output_dir, 'success_rates.png'))
        plt.close()

        # Plot average execution times
        plt.figure(figsize=(15,10))
        plt.barh(repo_workflows, avg_execution_times)
        plt.xlabel('Average Execution Time (s)')
        plt.ylabel('Repository-Workflow')
        plt.axvline(x=overall_stats['median_execution_time'], color='green', label='Median Execution Time')
        plt.axvline(x=overall_stats['average_execution_time'], color='red', label='Average Execution Time')

        plt.xticks(list(plt.xticks()[0]) + [overall_stats['median_execution_time']])
        plt.xticks(list(plt.xticks()[0]) + [overall_stats['average_execution_time']])
        plt.title('Average Execution Times for each Repository-Workflow')
        plt.tight_layout()
        plt.savefig(os.path.join(self.config.output_dir, 'avg_execution_times.png'))
        plt.close()
