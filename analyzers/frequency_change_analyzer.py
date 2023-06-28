"""Analyzes the frequency change of files"""
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
    frequency_change = []

    # Extract the relevant metrics and closing times
    for item in data:
        releases.append(item['releases']['count'])
        closed_pull_requests.append(item['pull_requests']['count_closed'])
        commits.append(item['commits']['count'])
        contributors.append(item['contributors']['count'])
        issues.append(item['issues']['count'])

        total_times_changed_list = []
        for file_change in item['files']["file_change_count"]:
            total_times_changed_list.append(file_change[list(file_change.keys())[0]]["total_times_changed"])

        frequency_change.append(np.mean(total_times_changed_list))

    # Plotting each metric against average closing time
    metrics = [closed_pull_requests, commits, contributors, issues, releases]
    metric_names = ['# closed pull requests', '# commits', '# contributors', '# issues', '# releases']

    for i, metric in enumerate(metrics):
        correlation, _ = spearmanr(frequency_change, metric)

        plt.figure()
        plt.scatter(frequency_change, metric)
        plt.xlabel('Average Closing Time for Issues')
        plt.ylabel(metric_names[i])
        plt.title(metric_names[i] + ' vs. average frequency change of files')

    plt.show()
