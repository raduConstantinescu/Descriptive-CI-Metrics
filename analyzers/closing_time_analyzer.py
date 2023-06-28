"""Analyzes the closing time of issues"""
import json

import matplotlib.pyplot as plt
import numpy as np
from scipy.stats import spearmanr

# Load data from the JSON file
if __name__ == '__main__':
    with open('../result.json', encoding='utf-8') as file:
        data = json.load(file)

    # Initialize lists to store metrics and average closing times
    closed_pull_requests = []
    commits = []
    contributors = []
    issues = []
    releases = []
    closing_times = []

    # Extract the relevant metrics and closing times
    for item in data:
        if len(item['issues']['closing_time']) != 0:
            releases.append(item['releases']['count'])
            closed_pull_requests.append(item['pull_requests']['count_closed'])
            commits.append(item['commits']['count'])
            contributors.append(item['contributors']['count'])
            issues.append(item['issues']['count'])
            closing_times.append(np.mean(item['issues']['closing_time']))

    # Plotting each metric against average closing time
    metrics = [closed_pull_requests, commits, contributors, issues, releases]
    metric_names = ['# closed pull requests', '# commits', '# contributors', '# issues', '# releases']

    for i, metric in enumerate(metrics):
        correlation, _ = spearmanr(closing_times, metric)

        plt.figure()
        plt.scatter(closing_times, metric)
        plt.xlabel('Average Closing Time for Issues')
        plt.ylabel(metric_names[i])
        plt.title(metric_names[i] + ' vs. average closing time for bug reports')

    plt.show()
