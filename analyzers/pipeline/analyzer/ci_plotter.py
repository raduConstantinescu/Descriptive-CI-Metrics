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

        # we will change success rates with breakage rates
        success_rates = [value['success_rate'] for value in data.values()]
        breakage_rates = [value['breakages_rate'] for value in data.values()]
        avg_execution_times = [value['average_execution_time'] for value in data.values()]
        median_execution_times = [value['median_execution_time'] for value in data.values()]

        # Create a new directory if it doesn't exist
        if not os.path.exists(self.config.output_dir):
            os.makedirs(self.config.output_dir)

        # Plot success rates
        plt.figure(figsize=(15,10))
        # can we have 2 decimal floats for the bar plot
        plt.barh(repo_workflows, breakage_rates)
        plt.xlabel('Breakage Rate')
        plt.ylabel('Repository-Workflow')
        plt.title('Breakage Rates for each Repository-Workflow')
        plt.xticks(list(plt.xticks()[0]) + [overall_stats['median_breakages_rate']])
        plt.axvline(x=overall_stats['median_breakages_rate'], color='green', label='Median Breakage Rate')
        plt.tight_layout()  # Ensure labels are not cut off
        plt.savefig(os.path.join(self.config.output_dir, 'breakage_rates.png'))
        plt.close()

        # Plot median execution times
        plt.figure(figsize=(15,10))
        plt.barh(repo_workflows, median_execution_times)
        plt.xlabel('Median Execution Time (s)')
        plt.ylabel('Repository-Workflow')
        plt.axvline(x=overall_stats['median_execution_time'], color='green', label='Median Execution Time')

        plt.xticks(list(plt.xticks()[0]) + [overall_stats['median_execution_time']])


        plt.title('Median Execution Times for each Repository-Workflow')
        plt.tight_layout()
        plt.savefig(os.path.join(self.config.output_dir, 'median_execution_times.png'))
        plt.close()
