from collections import Counter

from project_maturity_v2.utils import extract_data_from_json
import matplotlib.pyplot as plt
from datetime import datetime

class PullRequestGrowthAnalyzer():
    def __init__(self):
        self.data = extract_data_from_json('../outputs_v2/pull_request_data.json')
        self.maturity_info = extract_data_from_json('../outputs_v2/repo_maturity.json')

    def analyze(self):
        mature_prs, immature_prs = self.cluster_pull_requests()

        # Extract the creation dates for mature and immature projects
        mature_creation_dates = [datetime.strptime(pr['created_at'], "%Y-%m-%dT%H:%M:%S").date() for pr in mature_prs]
        immature_creation_dates = [datetime.strptime(pr['created_at'], "%Y-%m-%dT%H:%M:%S").date() for pr in
                                   immature_prs]

        # Count the occurrences of each creation date for mature and immature projects
        mature_counts = Counter(mature_creation_dates)
        immature_counts = Counter(immature_creation_dates)

        # Calculate the cumulative counts for mature and immature projects
        cumulative_counts_mature = []
        cumulative_counts_immature = []
        mature_cumulative_count = 0
        immature_cumulative_count = 0

        # Iterate over the dates in ascending order
        for date in sorted(set(mature_creation_dates + immature_creation_dates)):
            mature_cumulative_count += mature_counts[date]
            immature_cumulative_count += immature_counts[date]

            # Adjust the counts based on the sample size
            mature_cumulative_count_adjusted = mature_cumulative_count / len(mature_prs)
            immature_cumulative_count_adjusted = immature_cumulative_count / len(immature_prs)

            cumulative_counts_mature.append(mature_cumulative_count_adjusted)
            cumulative_counts_immature.append(immature_cumulative_count_adjusted)

        plt.figure(figsize=(8, 8))
        # Plot the cumulative count of pull requests against the dates for both mature and immature projects
        plt.plot(sorted(set(mature_creation_dates + immature_creation_dates)), cumulative_counts_mature,
                 label='Mature Projects', color='green')
        plt.plot(sorted(set(mature_creation_dates + immature_creation_dates)), cumulative_counts_immature,
                 label='Immature Projects', color='orange')
        plt.xlabel('Date')
        plt.ylabel('Cumulative Count of Pull Requests')
        plt.title('Growth of the Number of Pull Requests over Time')
        plt.xticks(rotation=45)
        plt.legend()
        plt.savefig('visualizations/pull_request_number_growth')
        plt.show()


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

PullRequestGrowthAnalyzer().analyze()