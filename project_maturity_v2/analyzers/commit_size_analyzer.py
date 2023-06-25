import ast
import calendar
import itertools
import statistics
from datetime import datetime, timedelta

from project_maturity_v2.utils import extract_data_from_json
import numpy as np
import matplotlib.pyplot as plt


class CommitSizeAnalyzer():
    def __init__(self):
        self.data = extract_data_from_json('../outputs_v2/repo_data.json')
        self.maturity_info = extract_data_from_json('../outputs_v2/repo_maturity.json')
        self.mature_repos, self.immature_repos = self.cluster_repostiories()

    def analyze(self):
        average_code_frequency_mature, average_additions_mature, average_deletions_mature, average_commit_count_mature = self.average_out(self.mature_repos)
        average_code_frequency_immature, average_additions_immature, average_deletions_immature, average_commit_count_immature = self.average_out(self.immature_repos)

        self.analyze_code_frequency_comparison(average_code_frequency_mature, average_code_frequency_immature)
        self.plot_bar_plot_deletions_additions(average_additions_mature, average_additions_immature, average_deletions_mature, average_deletions_immature)


    def cluster_repostiories(self):

        def reverse_array(arr):
            return arr[::-1]


        mature_repos = {}
        immature_repos = {}
        for repo_name, repo_data in self.data.items():
            if repo_name not in self.maturity_info.keys():
                continue
            if self.maturity_info[repo_name] is True:
                mature_repos[repo_name] = repo_data
                mature_repos[repo_name]["weekly_code_frequency"] = reverse_array(ast.literal_eval(repo_data["weekly_code_frequency"]))
                mature_repos[repo_name]["weekly_code_additions"] = reverse_array(ast.literal_eval(repo_data["weekly_code_additions"]))
                mature_repos[repo_name]["weekly_code_deletions"] = reverse_array(ast.literal_eval(repo_data["weekly_code_deletions"]))
                mature_repos[repo_name]["weekly_commit_count_last_year"] = reverse_array(ast.literal_eval(repo_data["weekly_commit_count_last_year"]))
            else:
                immature_repos[repo_name] = repo_data
                immature_repos[repo_name]["weekly_code_frequency"] = reverse_array(ast.literal_eval(repo_data["weekly_code_frequency"]))
                immature_repos[repo_name]["weekly_code_additions"] =reverse_array( ast.literal_eval(repo_data["weekly_code_additions"]))
                immature_repos[repo_name]["weekly_code_deletions"] = reverse_array(ast.literal_eval(repo_data["weekly_code_deletions"]))
                immature_repos[repo_name]["weekly_commit_count_last_year"] = reverse_array(ast.literal_eval(repo_data["weekly_commit_count_last_year"]))

        return mature_repos, immature_repos

    # newest to oldes counts
    def average_out(self, repos):

        def average_arrays(array_list):
            min_length = min(len(arr) for arr in array_list)
            max_length = max(len(arr) for arr in array_list)
            print(min_length)
            print(max_length)
            padded_arrays = [arr + [0] * (max_length - len(arr)) for arr in array_list]
            averages = [statistics.mean(elements) for elements in zip(*padded_arrays)]
            return averages


        code_frequencies = []
        code_additions = []
        code_deletions = []
        commit_count = []
        for repo_name, repo_data in repos.items():
            code_frequencies.append(repo_data["weekly_code_frequency"])
            code_additions.append(repo_data["weekly_code_additions"])
            code_deletions.append(repo_data["weekly_code_deletions"])
            commit_count.append(repo_data["weekly_commit_count_last_year"])


        average_code_frequency = average_arrays( code_frequencies)
        average_additions = average_arrays(code_additions)
        average_deletions  = average_arrays(code_deletions)
        average_commit_count = average_arrays(commit_count)

        return average_code_frequency, average_additions, average_deletions, average_commit_count

    def analyze_code_frequency_comparison(self, average_code_frequency_mature, average_code_frequency_immature):
        def reverse_array(arr):
            return arr[::-1]

        print(average_code_frequency_mature)
        print(average_code_frequency_immature)

        average_code_frequency_mature = reverse_array(average_code_frequency_mature)
        average_code_frequency_immature = reverse_array(average_code_frequency_immature)


        self.plot_cummulative_sum(average_code_frequency_mature, average_code_frequency_immature)
        self.plot_bar_plot(average_code_frequency_mature, average_code_frequency_immature)

    def plot_cummulative_sum(self,mature, immature):
        # Determine the size difference between the arrays
        size_difference = len(mature) - len(immature)

        # Generate the x-axis values based on the data size, accounting for the size difference
        x_mature = np.arange(len(mature))
        x_immature = np.arange(size_difference, size_difference + len(immature))

        # Create a figure and axes
        fig, ax = plt.subplots()

        # Compute the cumulative sums for the arrays
        cumulative_mature = np.cumsum(mature)
        cumulative_immature = np.cumsum(immature)

        color_mature = "#a8b6a1"
        color_immature = '#71253D'

        # Plot the stacked area plot
        ax.fill_between(x_mature, 0, cumulative_mature, label='Mature', color=color_mature, alpha=0.7)
        ax.fill_between(x_immature, 0, cumulative_immature, label='Immature', color=color_immature, alpha=0.7)

        # Set a title for the plot
        ax.set_title('Cumulative Weekly Code Churn for Mature and Immature projects')

        # Set labels for the x-axis and y-axis
        ax.set_xlabel('Time')
        ax.set_ylabel('Cumulative Weekly Code Churn')

        # Add a legend
        ax.legend()

        # Display the plot
        plt.show()

    def plot_bar_plot(self, mature, immature):
        # Convert lists to NumPy arrays
        mature = np.array(mature)
        immature = np.array(immature)# Determine the length of the longer array
        # Determine the length of the longer array
        min_length = min(len(mature), len(immature))

        # Determine the number of groups
        num_groups = min_length // 52
        print(num_groups)

        # Group the churn values by 26 and calculate the average for each group
        grouped_mature = np.mean(
            mature[:num_groups * 52].reshape(num_groups, 52), axis=1)
        grouped_immature = np.mean(
            immature[:num_groups * 52].reshape(num_groups, 52), axis=1)

        # Generate the x-axis values for the grouped bars
        x = np.arange(num_groups)
        # Calculate the starting date for the x-axis labels
        start_date = datetime.now() - timedelta(weeks=num_groups * 52)

        labels = ["2004", "2005", "2006", "2007", "2008", "2009", "2010", "2011", "2012", "2013", "2014", "2015", "2016", "2017", "2018", "2019", "2020", "2021", "2022", "2023"]

        # Create a figure and axes
        fig, ax = plt.subplots(figsize=(8, 6))

        # Set the width of each bar
        bar_width = 0.35

        # Plot the bars for "mature" category
        ax.bar(x, grouped_mature, width=bar_width, label='Mature projects')

        # Plot the bars for "immature" category, shifted by bar_width
        ax.bar(x + bar_width, grouped_immature, width=bar_width, label='Immature projects')

        # Set a title for the plot
        ax.set_title('Yearly Average Number of Code Changes')

        # Set labels for the x-axis and y-axis
        ax.set_xlabel('Time')
        ax.set_ylabel('Average Yearly Code Churn')

        # Set the x-axis tick positions and labels
        ax.set_xticks(np.arange(0, num_groups))
        ax.set_xticklabels(labels, rotation=45, ha='right')

        # Add a legend
        ax.legend()

        plt.savefig('visualizations/avg_yearly_code_churn')
        # Display the plot
        plt.tight_layout()
        plt.show()

    def plot_bar_plot_deletions_additions(self, mature_additions, immature_additions, mature_deletions, immature_deletions):
        def reverse_array(arr):
            return arr[::-1]

        mature_additions = reverse_array(mature_additions)
        immature_additions = reverse_array(immature_additions)
        mature_deletions = reverse_array(mature_deletions)
        immature_deletions = reverse_array(immature_deletions)
        # Convert lists to NumPy arrays
        mature_additions = np.array(mature_additions)
        immature_additions = np.array(immature_additions)
        mature_deletions = np.array(mature_deletions)
        immature_deletions = np.array(immature_deletions)

        min_length = min(len(mature_additions), len(immature_additions), len(mature_deletions), len(immature_deletions))

        # Determine the number of groups
        num_groups = min_length // 52
        print(num_groups)

        # Group the churn values by 26 and calculate the average for each group
        grouped_mature_additions = np.mean(
            mature_additions[:num_groups * 52].reshape(num_groups, 52), axis=1)
        grouped_immature_additions = np.mean(
            immature_additions[:num_groups * 52].reshape(num_groups, 52), axis=1)
        grouped_mature_deletions = np.mean(
            mature_deletions[:num_groups * 52].reshape(num_groups, 52), axis=1)
        grouped_immature_deletions = np.mean(
            immature_deletions[:num_groups * 52].reshape(num_groups, 52), axis=1)

        # Generate the x-axis values for the grouped bars
        x = np.arange(num_groups)

        labels = ["2004", "2005", "2006", "2007", "2008", "2009", "2010", "2011", "2012", "2013", "2014", "2015", "2016", "2017", "2018", "2019", "2020", "2021", "2022", "2023"]

        # Create a figure and axes
        fig, ax = plt.subplots(figsize=(8, 6))

        # Set the width of each bar
        bar_width = 0.35

        # Plot the bars for "mature" category (additions)
        ax.bar(x, grouped_mature_additions, width=bar_width, label='Mature project additions')

        # Plot the bars for "mature" category (deletions)
        ax.bar(x, grouped_mature_deletions, width=bar_width, label='Mature project deletions')

        # Plot the bars for "immature" category (additions)
        ax.bar(x + bar_width, grouped_immature_additions, width=bar_width, label='Immature project additions')

        # Plot the bars for "immature" category (deletions)
        ax.bar(x + bar_width, grouped_immature_deletions, width=bar_width, label='Immature project deletions')

        # Set a title for the plot
        ax.set_title('Yearly Average Number of Code Additions and Deletions')

        # Set labels for the x-axis and y-axis
        ax.set_xlabel('Time')
        ax.set_ylabel('Average Yearly Code Churn')

        # Set the x-axis tick positions and labels
        ax.set_xticks(np.arange(0, num_groups))
        ax.set_xticklabels(labels, rotation=45, ha='right')

        # Add a legend
        ax.legend()

        # Display the plot
        plt.savefig('visualizations/yearly_additions_deletions')
        # plt.tight_layout()
        plt.show()



CommitSizeAnalyzer().analyze()