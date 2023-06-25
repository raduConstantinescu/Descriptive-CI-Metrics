from datetime import datetime

from project_maturity_v2.utils import extract_data_from_json
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
import pandas as pd


class PullRequestsAnalyzer:
    def __init__(self):
        self.data = extract_data_from_json('../outputs_v2/pull_request_data.json')
        self.maturity_info = extract_data_from_json('../outputs_v2/repo_maturity.json')

    def analyze(self):
        analysis_results = []
        for repo_name, pull_requests in self.data.items():
            if repo_name not in self.maturity_info.keys():
                continue
            if len(pull_requests) == 0:
                continue
            pr_analysis = self.analyze_repo_pull_requests_basics(self.data[repo_name], repo_name)
            analysis_results.append(pr_analysis)
            # self.visualize_pull_request_size_over_time(repo_name)

        self.analyze_merge_speed(analysis_results)
        self.merge_vs_closed(analysis_results)
        self.churn_close_to_zero()

    def analyze_merge_speed(self, analysis_results):
        mature_merge_speed = []
        immature_merge_speed = []
        for analysis in analysis_results:
            if analysis['mature'] is True:
                if analysis['average_merge_speed'] != -1:
                    mature_merge_speed.append(analysis['average_merge_speed'])
            else:
                if analysis['average_merge_speed'] != -1 and analysis['average_merge_speed'] != 0:
                    immature_merge_speed.append(analysis['average_merge_speed'])

        immature_merge_speed = immature_merge_speed[:len(mature_merge_speed)]

        # Combine the data into a single list
        all_merge_speeds = [mature_merge_speed, immature_merge_speed]
        # Define a custom color palette with transparency (alpha value)
        custom_palette = ["#a8b6a1", "#d5a6bd"]  # Replace with your desired colors and alpha values

        # Create labels for the categories
        labels = ['Mature Projects', 'Immature Projects']

        # Create the violin plot with the custom color palette
        sns.violinplot(data=all_merge_speeds, palette='Set2')

        # Set the labels for the x-axis
        plt.xticks([0, 1], labels)

        # Set the label for the y-axis
        plt.ylabel('Merge Speed')

        # Add a horizontal line at 0
        plt.axhline(0, color='red', linestyle='--')
        plt.title("Distribution of Average Merge Speeds")
        plt.savefig('visualizations/merge_speeds_violin')
        # Display the plot
        plt.show()

    def merge_vs_closed(self, analysis_results):

        merged_mature = []

        merged_immature = []
        closed_not_merged_mature = []
        closed_not_merged_immature = []
        open_prs_mature = []
        open_prs_immature = []
        total_mature = []
        total_immature = []
        percentage_merged_mature = []
        percentage_merged_immature = []
        percentage_closed_not_merged_mature = []
        percentage_closed_not_merged_immature = []
        percentage_open_mature = []
        percentage_open_immature = []

        for pr in analysis_results:
            if pr['mature'] is True:
                total_mature.append(pr['prs_count'])
                merged_mature.append(pr['merged_prs'])
                closed_not_merged_mature.append(pr['closed_not_merged_prs'])
                open_prs_mature.append(pr['open_prs'])

                percentage_merged_mature.append((pr['merged_prs'] / pr['prs_count']) * 100)
                percentage_closed_not_merged_mature.append((pr['closed_not_merged_prs'] / pr['prs_count']) * 100)
                percentage_open_mature.append((pr['open_prs']/ pr['prs_count']) /100)

            else:
                total_immature.append(pr['prs_count'])
                merged_immature.append(pr['merged_prs'])
                closed_not_merged_immature.append(pr['closed_not_merged_prs'])
                open_prs_immature.append(pr['open_prs'])

                if pr['prs_count'] == 0:
                    percentage_merged_immature.append(0)
                    percentage_closed_not_merged_immature.append(0)
                    percentage_open_immature.append(0)
                else:
                    percentage_merged_immature.append((pr['merged_prs'] / pr['prs_count']) * 100)
                    percentage_closed_not_merged_immature.append((pr['closed_not_merged_prs'] / pr['prs_count']) * 100)
                    percentage_open_immature.append((pr['open_prs'] / pr['prs_count']) / 100)




        # overall_merged_mature = sum(percentage_merged_mature) / len(percentage_merged_mature)
        # overall_open_mature = sum(percentage_open_mature) / len(percentage_open_mature)
        # overall_closed_not_merged_mature = sum(percentage_closed_not_merged_mature)/len(percentage_closed_not_merged_mature)
        #
        # overall_merged_immature = sum(percentage_merged_immature) / len(percentage_merged_immature)
        # overall_open_immature = sum(percentage_open_immature) / len(percentage_open_immature)
        # overall_closed_not_merged_immature = sum(percentage_closed_not_merged_immature) / len(
        #     percentage_closed_not_merged_immature)
        #

        overall_merged_mature = sum(merged_mature) / sum(total_mature) * 100
        print(f"Overall merged mature: {overall_merged_mature}")

        overall_merged_immature = sum(merged_immature) / sum(total_immature) * 100
        print(f"Overall merged immature: {overall_merged_immature}")

        overall_closed_not_merged_mature = sum(closed_not_merged_mature) / sum(total_mature) * 100
        overall_closed_not_merged_immature = sum(closed_not_merged_immature) / sum(total_mature) * 100
        print(f"Overall closed not merged mature: {overall_closed_not_merged_mature}")

        print(f"Overall closed not merged immature: {overall_closed_not_merged_immature}")

        overall_open_mature = sum(open_prs_mature) / sum(total_mature) * 100
        overall_open_immature = sum(open_prs_immature) / sum(total_immature) * 100
        print(f"Overall open immature: {overall_open_immature}")
        print(f"Overall open mature: {overall_open_mature}")

    def analyze_repo_pull_requests_basics(self, pull_requests, repo_name):
        merged_count = 0
        closed_not_merged_count = 0
        open_count = 0
        merge_times = []
        total_merge_time = 0


        for pr in pull_requests:
            created_at = datetime.fromisoformat(pr['created_at'])

            if pr['merged_at'] is not None:
                merged_at = datetime.fromisoformat(pr['merged_at'])
            else:
                merged_at = None

            if pr['closed_at'] is not None:
                closed_at = datetime.fromisoformat(pr['closed_at'])
            else:
                closed_at = None

            if pr['merged']:
                merged_count += 1
                merge_time = (merged_at - created_at).total_seconds()
                merge_times.append(merge_time)
                total_merge_time += merge_time
            elif pr['closed_at'] is not None:
                closed_not_merged_count += 1
            else:
                open_count += 1

        average_merge_speed = total_merge_time / merged_count if merged_count > 0 else -1

        analysis = {
            'mature': self.maturity_info[repo_name] if repo_name in self.maturity_info.keys() else repo_name,
            'prs_count': len(pull_requests),
            'average_merge_speed': average_merge_speed,
            'merged_prs': merged_count,
            'closed_not_merged_prs': closed_not_merged_count,
            'open_prs': open_count,
            'merge_times': merge_times
        }

        return analysis

    def visualize_pull_request_size_over_time(self, repo_name):
        x = []
        y = []
        if len(self.data[repo_name]) ==0:
            return
        for pr in self.data[repo_name]:

            created_at = datetime.strptime(pr["created_at"], "%Y-%m-%dT%H:%M:%S")
            x.append(created_at)
            y.append(pr["additions"] - pr["deletions"])

        plt.plot(x, y)
        plt.xlabel("Created At")
        plt.ylabel("Pull Request Size (Churn)")
        plt.title(f"Variation of Pull Request Size Over Time for {self.maturity_info[repo_name]} repo {repo_name}")
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.show()

    def churn_close_to_zero(self):

        mature_churns = []
        immature_churns = []
        for repo_name, prs in self.data.items():
            equal_churns_count = 0
            if repo_name not in self.maturity_info.keys():
                continue
            maturity = self.maturity_info[repo_name]
            for pr in prs:
                if pr['additions'] - pr['deletions'] < 2:
                    equal_churns_count+=1

            if self.maturity_info[repo_name] is True:
                mature_churns.append(equal_churns_count)
            else:
                immature_churns.append(equal_churns_count)

        print(mature_churns)
        print(np.median(mature_churns))
        print(immature_churns)
        print(np.median(immature_churns))

    def pull_request_sizes(self):
        # Group pull requests based on project maturity
        mature_pull_requests, immature_pull_requests = self.cluster_pull_requests()
        # Extract the created_at timestamp and churn for each pull request
        mature_dates = []
        mature_churn = []
        mature_files_count = []
        mature_commit_count = []

        for pr in mature_pull_requests:
            created_at = datetime.strptime(pr["created_at"], "%Y-%m-%dT%H:%M:%S")
            mature_dates.append(created_at)
            mature_churn.append(pr["additions"] - pr["deletions"])
            mature_files_count.append(pr['changed_files_count'])
            mature_commit_count.append(pr['commit_count'])

        immature_dates = []
        immature_churn = []
        immature_files_count = []
        immature_commit_count = []

        for pr in immature_pull_requests:
            created_at = datetime.strptime(pr["created_at"], "%Y-%m-%dT%H:%M:%S")
            immature_dates.append(created_at)
            immature_churn.append(pr["additions"] - pr["deletions"])
            immature_files_count.append(pr['changed_files_count'])
            immature_commit_count.append(pr['commit_count'])

        self.plot_churn_over_time(mature_churn, mature_dates, immature_churn, immature_dates)
        # self.analyze_size_of_prs(mature_churn, immature_churn)
        # self.analyze_commit_and_file_count("Mature", mature_churn, mature_files_count, mature_commit_count)
        # self.analyze_commit_and_file_count("Immature", immature_churn, immature_files_count, immature_commit_count)

    def cluster_pull_requests(self):
        mature_pull_requests = []
        immature_pull_requests = []

        for repo_name, prs in self.data.items():
            if repo_name not in self.maturity_info.keys():
                continue
            if len(prs) == 0:
                continue
            if self.maturity_info[repo_name] is True:
                mature_pull_requests.extend(prs)
            else:
                immature_pull_requests.extend(prs)

        print(f" We analyzed {len(mature_pull_requests)} mature pull requests")
        print(f" We analyzed {len(immature_pull_requests)} immature pull requests")

        return mature_pull_requests, immature_pull_requests

    def plot_churn_over_time(self, mature_churn, mature_dates, immature_churn, immature_dates):
        # Convert the dates to a pandas datetime format
        mature_dates = pd.to_datetime(mature_dates)
        immature_dates = pd.to_datetime(immature_dates)

        # Create a DataFrame using the dates and churn values
        mature_df = pd.DataFrame({'Dates': mature_dates, 'Churn': mature_churn})
        immature_df = pd.DataFrame({'Dates': immature_dates, 'Churn': immature_churn})

        # Set the Dates column as the index for each DataFrame
        mature_df.set_index('Dates', inplace=True)
        immature_df.set_index('Dates', inplace=True)

        # Resample the data at a weekly frequency and calculate the average churn
        mature_weekly_avg = mature_df.resample('W').mean()
        immature_weekly_avg = immature_df.resample('W').mean()

        # Plot the churn over time for mature and immature projects (weekly averages)
        plt.figure(figsize=(8, 6))
        plt.plot(mature_weekly_avg.index, mature_weekly_avg['Churn'], color='red', label="Mature Projects")
        plt.plot(immature_weekly_avg.index, immature_weekly_avg['Churn'], color='orange', label="Immature Projects")
        plt.xlabel("Date")
        plt.ylabel("Average Churn")
        plt.title("Average Churn of Pull Requests Over The Last 6 Months (Weekly)")
        plt.legend()
        plt.savefig('visualizations/weekly churn of pull requests')
        plt.show()

    def analyze_size_of_prs(self, mature_churn, immature_churn):
        mature_bug_fixes = 0
        immature_bug_fixes = 0

        for churn in mature_churn:
            if churn == 0:
                mature_bug_fixes += 1

        for churn in immature_churn:
            if churn == 0:
                immature_bug_fixes += 1

        print(f"Mature prs with churn 0: {(mature_bug_fixes / len(mature_churn)) * 100}")
        print(f"Immature prs with churn 0: {(immature_bug_fixes / len(immature_churn)) * 100}")

        average_mature_churn = np.mean(mature_churn)
        average_immature_churn = np.mean(immature_churn)

        above_average_mature = sum(1 for pr in mature_churn if pr > average_mature_churn)
        above_average_immature = sum(1 for pr in immature_churn if pr > average_immature_churn)

        print(f"Average mature churn: {average_mature_churn}")
        print(f"Average immature churn: {average_immature_churn}")
        print(f"Percentage of above average mature churn {(above_average_mature / len(mature_churn)) * 100}")
        print(f"Percentage of above average mature churn {(above_average_immature / len(immature_churn)) * 100}")

    def analyze_commit_and_file_count(self, category, churn, file_count, commit_count):
        fc_lt = 0
        for fc in file_count:
            if fc == 1:
                fc_lt +=1

        cc_lt = 0
        for cc in commit_count:
            if cc == 1:
                cc_lt +=1

        print(category)
        print((fc_lt/len(file_count)) * 100)
        print((cc_lt/len(commit_count)) * 100)

    def pr_table_analysis(self):
        mature_pull_requests, immature_pull_requests = self.cluster_pull_requests()

        mature_data = self.analyze_repo_pull_requests_basics(mature_pull_requests, "mature")
        immature_data = self.analyze_repo_pull_requests_basics(immature_pull_requests[:len(mature_pull_requests)-1], "immature")


        del mature_data['merge_times']
        del immature_data['merge_times']

        print(mature_data)
        print(immature_data)

        # Extracting the relevant values
        mature_values = [mature_data['merged_prs'], mature_data['closed_not_merged_prs'], mature_data['open_prs']]
        immature_values = [immature_data['merged_prs'], immature_data['closed_not_merged_prs'],
                           immature_data['open_prs']]

        # Plotting the bar chart
        labels = ['Merged PRs', 'Closed PRs', 'Open PRs']
        x = range(len(labels))
        width = 0.35

        fig, ax = plt.subplots()
        rects1 = ax.bar(x, mature_values, width, label='Mature')
        rects2 = ax.bar([i + width for i in x], immature_values, width, label='Immature')

        # Adding labels, title, and legend
        ax.set_xlabel('PR Status')
        ax.set_ylabel('Count')
        ax.set_title('PR Status Comparison for Mature and Immature Projects')
        ax.set_xticks([i + width / 2 for i in x])
        ax.set_xticklabels(labels)
        ax.legend()

        # Displaying the plot
        plt.show()



PullRequestsAnalyzer().pull_request_sizes()
