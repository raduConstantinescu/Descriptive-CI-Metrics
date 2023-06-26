import json
import os
import statistics
from datetime import datetime
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
from scipy import stats

from build_performance.stage.stage import PipelineStage
from build_performance.utils import load_json_data


class RepoBuildPerformanceClassifierConfig:
    def __init__(self, config):
        self.input_file = config["input_file"]
        self.output_file = config["output_file"]
        self.plots_dir = config["plots_dir"]
        self.stats_file = config["stats_file"]


class RepoBuildPerformanceClassifier(PipelineStage):
    def __init__(self, config):
        self.config = RepoBuildPerformanceClassifierConfig(config)

    def run(self):
        data = load_json_data(self.config.input_file)
        print("Running RepoBuildPerformanceClassifier")
        print(len(data))
        repo_build_performance = {}

        working_hour_categories = {
            'working_hours': {'total': 0, 'failures': 0},  # from 9am to 5pm
            'out_of_hours': {'total': 0, 'failures': 0}  # from 5pm to 9am
        }

        time_of_day_categories = {
            'early_morning': {'total': 0, 'failures': 0},  # 00:00 to 05:59
            'morning': {'total': 0, 'failures': 0},  # 06:00 to 11:59
            'afternoon': {'total': 0, 'failures': 0},  # 12:00 to 17:59
            'evening': {'total': 0, 'failures': 0},  # 18:00 to 23:59
        }

        days_of_week = {
            'Monday': {'total': 0, 'failures': 0},
            'Tuesday': {'total': 0, 'failures': 0},
            'Wednesday': {'total': 0, 'failures': 0},
            'Thursday': {'total': 0, 'failures': 0},
            'Friday': {'total': 0, 'failures': 0},
            'Saturday': {'total': 0, 'failures': 0},
            'Sunday': {'total': 0, 'failures': 0},
        }



        for repo in data:
            repo_build_performance[repo['repoName']] = {}
            # repo_build_performance[repo['repoName']]['metrics'] = repo['metrics']
            for workflow in repo['workflow']:
                repo_build_performance[repo['repoName']][workflow['name']] = {}
                repo_build_performance[repo['repoName']][workflow['name']]['quarter_data'] = False
                if len(workflow['runs_data']) != 1000:
                    repo_build_performance[repo['repoName']][workflow['name']]['quarter_data'] = True
                run_durations = []
                run_conclusions = []
                failures = 0
                successes = 0
                repo_build_performance[repo['repoName']][workflow['name']]['time_of_day'] = {key: value.copy() for
                                                                                             key, value in
                                                                                             time_of_day_categories.items()}
                repo_build_performance[repo['repoName']][workflow['name']]['working_hours'] = {key: value.copy() for
                                                                                               key, value in
                                                                                               working_hour_categories.items()}
                repo_build_performance[repo['repoName']][workflow['name']]['days_of_week'] = {key: value.copy() for
                                                                                              key, value in
                                                                                              days_of_week.items()}
                for run in workflow['runs_data']:
                    creation_time = datetime.strptime(run['created_at'], '%Y-%m-%dT%H:%M:%S')
                    hour = creation_time.hour
                    day_of_week = creation_time.strftime('%A')

                    # Update time_of_day categories
                    if 0 <= hour < 6:
                        category = 'early_morning'
                    elif 6 <= hour < 12:
                        category = 'morning'
                    elif 12 <= hour < 18:
                        category = 'afternoon'
                    else:
                        category = 'evening'

                    repo_build_performance[repo['repoName']][workflow['name']]['time_of_day'][category]['total'] += 1
                    if run['conclusion'] == 'failure':
                        repo_build_performance[repo['repoName']][workflow['name']]['time_of_day'][category][
                            'failures'] += 1

                    if 9 <= hour < 17:
                        category = 'working_hours'
                    else:
                        category = 'out_of_hours'

                    repo_build_performance[repo['repoName']][workflow['name']]['working_hours'][category]['total'] += 1
                    if run['conclusion'] == 'failure':
                        repo_build_performance[repo['repoName']][workflow['name']]['working_hours'][category][
                            'failures'] += 1

                    repo_build_performance[repo['repoName']][workflow['name']]['days_of_week'][day_of_week][
                        'total'] += 1
                    if run['conclusion'] == 'failure':
                        repo_build_performance[repo['repoName']][workflow['name']]['days_of_week'][day_of_week][
                            'failures'] += 1

                    # Duration logic
                    duration = datetime.strptime(run['updated_at'], '%Y-%m-%dT%H:%M:%S') - datetime.strptime(
                        run['created_at'], '%Y-%m-%dT%H:%M:%S')
                    run_durations.append(duration.total_seconds())
                    if run['conclusion'] == 'failure':
                        failures += 1
                    elif run['conclusion'] == 'success':
                        successes += 1
                    run_conclusions.append(run['conclusion'])
                # verification for division by zero
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

        # 1. High breakage rate, high median duration
        # 2. High breakage rate, low median duration
        # 3. Low breakage rate, high median duration
        # 4. Low breakage rate, low median duration

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

        os.makedirs(self.config.plots_dir, exist_ok=True)

        # Box plot for durations
        plt.figure(figsize=(10, 5))
        plt.boxplot(filtered_durations)
        plt.title('Box Plot of Workflow Durations')
        plt.ylabel('Duration (minutes)')
        median_val = np.median(filtered_durations)
        plt.axhline(median_val, color='r', linestyle='dashed', linewidth=2)  # Add median line
        plt.legend([f'Median: {median_val:.2f}'])
        plt.savefig(os.path.join(self.config.plots_dir, 'box_plot.png'))
        plt.show()

        # Violin plot for durations
        plt.figure(figsize=(10, 5))
        plt.violinplot(filtered_durations)
        plt.title('Violin Plot of Workflow Durations')
        plt.ylabel('Duration (minutes)')
        median_val = np.median(filtered_durations)
        plt.axhline(median_val, color='r', linestyle='dashed', linewidth=2)  # Add median line
        plt.legend([f'Median Duration: {median_val:.2f}'])
        plt.savefig(os.path.join(self.config.plots_dir, 'violin_plot.png'))
        plt.show()

        # Plot breakage histogram
        plt.figure(figsize=(10, 5))
        plt.hist(filtered_breakages, bins='auto')
        plt.title('Workflow Breakages Histogram')
        plt.xlabel('Breakage Rate')
        plt.ylabel('Frequency')
        median_val = np.median(filtered_breakages)
        plt.axvline(median_val, color='r', linestyle='dashed', linewidth=2)  # Add median line
        plt.legend([f'Median Breakage Rate: {median_val:.2f}'])
        plt.savefig(os.path.join(self.config.plots_dir, 'histogram.png'))
        plt.show()

        # Compute median values
        median_duration = np.median(filtered_durations)
        median_breakage = np.median(filtered_breakages)
        # add to the stats file
        stats['median_duration_filtered'] = median_duration
        stats['median_breakage_filtered'] = median_breakage

        with open(self.config.stats_file, 'w') as json_file:
            json.dump(stats, json_file, indent=4)

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

        plt.figure(figsize=(10, 5))

        # Limit x-axis between 0 and 30
        plt.xlim(0, 30)

        # Adjust the limit of the y-axis
        plt.ylim(0, 0.6)

        plt.scatter(filtered_durations, filtered_breakages, color=colors, alpha=0.5)
        plt.axhline(median_breakage, color='k', linestyle='--')
        plt.axvline(median_duration, color='k', linestyle='--')

        # Add labels with increased font size
        plt.xlabel('Median Duration (minutes)', fontsize=14)
        plt.ylabel('Median Breakage Rate', fontsize=14)

        plt.title('Workflows Performance Clustering', fontsize=16)
        plt.legend([f'Median Duration: {median_duration:.2f} minutes', f'Median Breakage Rate: {median_breakage:.2f}'])
        plt.grid(True)
        plt.savefig(os.path.join(self.config.plots_dir, 'scatter_plot.png'))
        plt.show()

        print(f'Quadrant counts: {quadrants}')

        # Classify each workflow into a quadrant
        for repo in repo_build_performance:
            for workflow in repo_build_performance[repo]:
                duration = repo_build_performance[repo][workflow]['median_duration'] / 60  # Convert to minutes
                breakage = repo_build_performance[repo][workflow]['breakage_rate']

                if duration > median_duration and breakage > median_breakage:
                    repo_build_performance[repo][workflow]['quadrant'] = 'HBHT'
                elif duration <= median_duration and breakage > median_breakage:
                    repo_build_performance[repo][workflow]['quadrant'] = 'HBLT'
                elif duration > median_duration and breakage <= median_breakage:
                    repo_build_performance[repo][workflow]['quadrant'] = 'LBHT'
                else:
                    repo_build_performance[repo][workflow]['quadrant'] = 'LBLT'

        with open(self.config.output_file, 'w') as json_file:
            json.dump(repo_build_performance, json_file, indent=4)

        self.visualize_languages_by_quadrant(repo_build_performance, data)
        self.visualize_quadrant_metrics(repo_build_performance, data)
        self.visualize_by_moment_of_execution(repo_build_performance, data)


    def visualize_by_moment_of_execution(self, repo_build_performance, data):
        quadrants = ['HBHT', 'HBLT', 'LBHT', 'LBLT']

    def visualize_quadrant_metrics(self, repo_build_performance, data):
        # Define metrics to be visualized
        metrics = ['stars', 'contributors', 'commits']
        # Get metric mean for each quadrant
        quadrant_metrics = {
            'HBHT': {metric: [] for metric in metrics},
            'HBLT': {metric: [] for metric in metrics},
            'LBHT': {metric: [] for metric in metrics},
            'LBLT': {metric: [] for metric in metrics}
        }

        for repo in data:
            for workflow in repo['workflow']:
                quadrant_of_workflow = repo_build_performance[repo['repoName']][workflow['name']]['quadrant']
                for metric in metrics:
                    quadrant_metrics[quadrant_of_workflow][metric].append(repo['metrics'][metric])

        # Calculate mean for each metric in each quadrant
        for quadrant, metrics in quadrant_metrics.items():
            for metric, values in metrics.items():
                quadrant_metrics[quadrant][metric] = statistics.mean(values)

        os.makedirs(self.config.plots_dir, exist_ok=True)

        # Create a single figure with three subplots for each metric
        fig, axs = plt.subplots(3, 1, figsize=(10, 30))
        fig.suptitle('Mean of Stars, Contributors, and Commits in Each Quadrant')

        def make_autopct(values):
            def my_autopct(pct):
                total = sum(values)
                val = int(round(pct * total / 100.0))
                return '{p:.1f}%  ({v:d})'.format(p=pct, v=val)

            return my_autopct

        for index, metric in enumerate(metrics):
            ax = axs[index]
            values = [quadrant_metrics[quadrant][metric] for quadrant in quadrant_metrics]
            ax.pie(values, labels=list(quadrant_metrics.keys()), autopct=make_autopct(values), startangle=90)
            ax.axis('equal')
            ax.set_title(f'Mean {metric.capitalize()}')

        plt.tight_layout(rect=[0, 0.03, 1, 0.95])  # to ensure the suptitle and subplots do not overlap
        plt.savefig(os.path.join(self.config.plots_dir, 'quadrant_metrics.png'))
        plt.show()

    def visualize_languages_by_quadrant(self, repo_build_performance, data):
        quadrant_languages = {
            'HBHT': {},
            'HBLT': {},
            'LBHT': {},
            'LBLT': {}
        }

        workflows_by_language = {}
        repos_by_language = {}

        for repo in data:
            for workflow in repo['workflow']:
                quadrant_of_workflow = repo_build_performance[repo['repoName']][workflow['name']]['quadrant']
                language_of_repo = repo['metrics']['language']
                if language_of_repo not in workflows_by_language:
                    workflows_by_language[language_of_repo] = 0
                workflows_by_language[language_of_repo] += 1
                if language_of_repo not in repos_by_language:
                    repos_by_language[language_of_repo] = 0
                repos_by_language[language_of_repo] += 1
                if language_of_repo not in quadrant_languages[quadrant_of_workflow]:
                    quadrant_languages[quadrant_of_workflow][language_of_repo] = 0
                quadrant_languages[quadrant_of_workflow][language_of_repo] += 1

        os.makedirs(self.config.plots_dir, exist_ok=True)

        fig, axs = plt.subplots(2, 2, figsize=(20, 20))
        fig.suptitle('Languages in Quadrants')

        for index, (quadrant, languages) in enumerate(quadrant_languages.items()):
            ax = axs[index // 2, index % 2]
            ax.pie(list(languages.values()), labels=list(languages.keys()), autopct='%1.1f%%', startangle=90)
            ax.axis('equal')
            ax.set_title(f'{quadrant}')

        plt.tight_layout(rect=[0, 0.03, 1, 0.95])
        plt.savefig(os.path.join(self.config.plots_dir, 'quadrant_languages.png'))
        plt.show()

        print(f'Workflows by language: {workflows_by_language}')
        print(f'Repos by language: {repos_by_language}')


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

