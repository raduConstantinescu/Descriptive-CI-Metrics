import json
import statistics
from datetime import datetime
import matplotlib.pyplot as plt
import numpy as np
import altair as alt
import altair as alt
import pandas as pd
import numpy as np

from build_performance.stage.stage import PipelineStage
from build_performance.utils import load_json_data, output_json_data


class RepoBuildPerformanceClassifierConfig:
    def __init__(self, config):
        self.input_file = config["input_file"]
        self.output_file = config["output_file"]
        self.stats_file = config["stats_file"]


class RepoBuildPerformanceClassifier(PipelineStage):
    def __init__(self, args, config):
        self.verbose = args.verbose
        self.config = RepoBuildPerformanceClassifierConfig(config)

    def run(self):
        data = load_json_data(self.config.input_file)
        print("Running RepoBuildPerformanceClassifier")
        print(len(data))
        repo_build_performance = {}
        for repo in data:
            repo_build_performance[repo['repoName']] = {}
            for workflow in repo['workflow']:
                repo_build_performance[repo['repoName']][workflow['name']] = {}
                repo_build_performance[repo['repoName']][workflow['name']]['quarter_data'] = False
                if len(workflow['runs_data']) != 1000:
                    repo_build_performance[repo['repoName']][workflow['name']]['quarter_data'] = True
                run_durations = []
                run_conclusions = []
                # lets also calculate 2 breakage rates here: failures / total runs and failures / successes + failures
                failures = 0
                successes = 0
                for run in workflow['runs_data']:
                    duration = datetime.strptime(run['updated_at'], '%Y-%m-%dT%H:%M:%S') - datetime.strptime(
                        run['created_at'], '%Y-%m-%dT%H:%M:%S')
                    run_durations.append(duration.total_seconds())
                    if run['conclusion'] == 'failure':
                        failures += 1
                    elif run['conclusion'] == 'success':
                        successes += 1
                    run_conclusions.append(run['conclusion'])
                # verifiy for division by zero
                breakage_rate = 0
                breakage_rate_all_events = 0
                if failures + successes != 0:
                    breakage_rate = failures / (failures + successes)
                if len(workflow['runs_data']) != 0:
                    breakage_rate_all_events = failures / len(workflow['runs_data'])

                repo_build_performance[repo['repoName']][workflow['name']]['breakage_rate'] = breakage_rate
                repo_build_performance[repo['repoName']][workflow['name']]['breakage_rate_all_events'] = breakage_rate_all_events
                repo_build_performance[repo['repoName']][workflow['name']]['run_durations'] = run_durations
                repo_build_performance[repo['repoName']][workflow['name']]['run_conclusions'] = run_conclusions
                median_duration = statistics.median(run_durations)
                repo_build_performance[repo['repoName']][workflow['name']]['median_duration'] = median_duration
                repo_build_performance[repo['repoName']][workflow['name']]['success'] = run_conclusions.count('success')
                repo_build_performance[repo['repoName']][workflow['name']]['failure'] = run_conclusions.count('failure')
                repo_build_performance[repo['repoName']][workflow['name']]['conclusion_set'] = list(
                    set(run_conclusions))
                repo_build_performance[repo['repoName']][workflow['name']]['conclusion_set_count'] = {}
                for conclusion in repo_build_performance[repo['repoName']][workflow['name']]['conclusion_set']:
                    repo_build_performance[repo['repoName']][workflow['name']]['conclusion_set_count'][
                        conclusion] = run_conclusions.count(conclusion)

        with open(self.config.output_file, 'w') as json_file:
            json.dump(repo_build_performance, json_file, indent=4)

        # # Calculate stats overall over all repositories - workflows
        stats = {}
        workflow_median_durations = []
        workflow_breakage_rates = []
        for repo in repo_build_performance:
            for workflow in repo_build_performance[repo]:
                workflow_median_durations.append(
                    repo_build_performance[repo][workflow]['median_duration'])
                workflow_breakage_rates.append(repo_build_performance[repo][workflow]['breakage_rate'])
        stats['median_duration'] = statistics.median(workflow_median_durations)
        stats['breakage_rate'] = statistics.median(workflow_breakage_rates)



        with open(self.config.stats_file, 'w') as json_file:
            json.dump(stats, json_file, indent=4)

        # Based on these stats lets classify the workflows on 4 quadrants
        # 1. High breakage rate, high median duration
        # 2. High breakage rate, low median duration
        # 3. Low breakage rate, high median duration
        # 4. Low breakage rate, low median duration

        # Prepare data for plotting
        duration_breakage_pairs = []

        for repo in repo_build_performance:
            for workflow in repo_build_performance[repo]:
                duration = repo_build_performance[repo][workflow]['median_duration'] / 60  # Convert to minutes
                breakage = repo_build_performance[repo][workflow]['breakage_rate']
                duration_breakage_pairs.append((duration, breakage))

        # Compute the IQR for durations
        durations = [pair[0] for pair in duration_breakage_pairs]
        Q1_duration = np.percentile(durations, 25)
        Q3_duration = np.percentile(durations, 75)
        IQR_duration = Q3_duration - Q1_duration

        # Identify outliers for durations
        lower_bound_duration = Q1_duration - 1.5 * IQR_duration
        upper_bound_duration = Q3_duration + 1.5 * IQR_duration

        # Filter outliers
        filtered_pairs = [pair for pair in duration_breakage_pairs if
                          lower_bound_duration <= pair[0] <= upper_bound_duration]

        filtered_durations = [pair[0] for pair in filtered_pairs]
        filtered_breakages = [pair[1] for pair in filtered_pairs]

        print(
            f'Removed {len(duration_breakage_pairs) - len(filtered_pairs)} outliers from durations and corresponding breakage rates')

        # Box plot for durations
        plt.figure(figsize=(10, 5))
        plt.boxplot(filtered_durations)
        plt.title('Box Plot of Workflow Durations')
        plt.ylabel('Duration (minutes)')
        median_val = np.median(filtered_durations)
        plt.axhline(median_val, color='r', linestyle='dashed', linewidth=2)  # Add median line
        plt.legend([f'Median: {median_val:.2f}'])
        plt.show()

        # Violin plot for durations
        plt.figure(figsize=(10, 5))
        plt.violinplot(filtered_durations)
        plt.title('Violin Plot of Workflow Durations')
        plt.ylabel('Duration (minutes)')
        median_val = np.median(filtered_durations)
        plt.axhline(median_val, color='r', linestyle='dashed', linewidth=2)  # Add median line
        plt.legend([f'Median: {median_val:.2f}'])
        plt.show()

        # Plot breakage histogram
        plt.figure(figsize=(10, 5))
        plt.hist(filtered_breakages, bins='auto')
        plt.title('Histogram of Workflow Breakages')
        plt.xlabel('Breakage Rate')
        plt.ylabel('Frequency')
        median_val = np.median(filtered_breakages)
        plt.axvline(median_val, color='r', linestyle='dashed', linewidth=2)  # Add median line
        plt.legend([f'Median: {median_val:.2f}'])
        plt.show()



        # Compute median values
        median_duration = np.median(filtered_durations)
        median_breakage = np.median(filtered_breakages)

        # Define quadrants
        quadrants = {
            'HBHT': 0,
            'HBLT': 0,
            'LBHT': 0,
            'LBLT': 0
        }

        colors = []

        # Classify each workflow into a quadrant
        for duration, breakage in filtered_pairs:
            if breakage > median_breakage and duration > median_duration:
                quadrants['HBHT'] += 1
                colors.append('r')
            elif breakage > median_breakage and duration <= median_duration:
                quadrants['HBLT'] += 1
                colors.append('y')
            elif breakage <= median_breakage and duration > median_duration:
                quadrants['LBHT'] += 1
                colors.append('y')
            else:
                quadrants['LBLT'] += 1
                colors.append('g')

        # Plot data
        plt.figure(figsize=(10, 5))
        plt.scatter(filtered_durations, filtered_breakages, color=colors, alpha=0.5)
        plt.axhline(median_breakage, color='k', linestyle='--')
        plt.axvline(median_duration, color='k', linestyle='--')
        plt.xlabel('Median Duration (minutes)')
        plt.ylabel('Breakage Rate')
        plt.title('Workflows by Build Performance: Duration vs Breakage Rate')
        plt.legend([f'Median Duration: {median_duration:.2f} minutes', f'Median Breakage Rate: {median_breakage:.2f}'])
        plt.grid(True)
        plt.show()

        print(f'Quadrant counts: {quadrants}')

    def remove_outliers(self, data):
        # Compute the IQR
        Q1 = np.percentile(data, 25)
        Q3 = np.percentile(data, 75)
        IQR = Q3 - Q1

        # Identify outliers
        lower_bound = Q1 - 1.5 * IQR
        upper_bound = Q3 + 1.5 * IQR
        outliers = [x for x in data if x < lower_bound or x > upper_bound]

        # Remove outliers
        filtered_data = [x for x in data if x >= lower_bound and x <= upper_bound]

        return filtered_data, outliers








