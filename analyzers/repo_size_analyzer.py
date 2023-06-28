"""Analyzes the repository size"""
import json

import matplotlib.pyplot as plt
from scipy.stats import spearmanr

if __name__ == '__main__':
    # matplotlib.use('TkAgg')  # Uncomment if you want to open the plot in a separate window
    # Load data from the JSON file
    with open('../result.json', encoding='utf-8') as file:
        data = json.load(file)

    # Extract the relevant metrics
    repository_size = []
    closed_pull_requests = []
    commits = []
    contributors = []
    issues = []
    releases = []

    for item in data:
        repository_size.append(item['size']['repos_size'])
        closed_pull_requests.append(item['pull_requests']['count_closed'])
        commits.append(item['commits']['count'])
        contributors.append(item['contributors']['count'])
        issues.append(item['issues']['count'])
        releases.append(item['releases']['count'])

    # Plotting the repository size against each metric
    metrics = [closed_pull_requests, commits, contributors, issues, releases]
    metric_names = ['# closed pull requests', '# commits', '# contributors', '# issues', '# releases']

    for i, metric in enumerate(metrics):
        correlation, _ = spearmanr(repository_size, metric)

        plt.figure()
        plt.scatter(repository_size, metric)
        plt.xlabel('Repository size')
        plt.ylabel(metric_names[i])
        plt.title(metric_names[i] + ' vs. repository size')

    plt.show()
