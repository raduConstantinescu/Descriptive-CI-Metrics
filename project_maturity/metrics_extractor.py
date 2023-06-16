import calendar
import json
import os
import time
from datetime import datetime, timedelta, date

from dotenv import load_dotenv

from utils import load_repos,was_repo_processed, save_data, save_processed

from github import RateLimitExceededException, Github


class MetricsExtractor:
    def __init__(self, github):
        self.g = github
        self.repos = load_repos("./output/immature_repos.txt")

    def extract(self):
        for repo_name in self.repos:
            if was_repo_processed(repo_name, "./output/immature_checked.txt"):
                print(repo_name + " was already processed")
                continue
            self.extract_metrics(repo_name)

    def extract_metrics(self, repo_name):
        print("Extracting metrics for: " + repo_name)
        while True:
            try:
                repo = self.g.get_repo(repo_name)
                metrics = {
                    "created_at": repo.created_at.isoformat(),
                    "updated_at": repo.updated_at.isoformat(),
                    "default_branch": repo.default_branch,
                    "language": repo.language,
                    "size": repo.size,
                    "has_wiki": repo.has_wiki,
                    "forks_count": repo.forks_count,
                    "stargazers_count": repo.stargazers_count,
                    "watchers_count": repo.watchers_count,
                    "open_issues_count": repo.open_issues_count,
                    "contributors_count": repo.get_contributors().totalCount,
                    "commits_count": repo.get_commits().totalCount,
                    "code_frequency": self.retrieve_code_frequency(repo),
                    "pull_requests": repo.get_pulls().totalCount,
                    "pull_requests_all_time": repo.get_pulls(state="all").totalCount
                }
                print("- saving data")
                save_data(repo_name, metrics, 'output/immature_repo_data.json')
                print("- adding repo to processed_pr_repos.txt")
                save_processed(repo_name, "./output/immature_checked.txt")
                break
            except RateLimitExceededException:
                print("Rate limit exceeded. Waiting for reset...")
                core_rate_limit = self.g.get_rate_limit().core
                reset_timestamp = calendar.timegm(core_rate_limit.reset.timetuple())
                sleep_time = reset_timestamp - calendar.timegm(
                    time.gmtime()) + 5  # add 5 seconds to be sure the rate limit has been reset
                time.sleep(sleep_time)
                # Retry the current search
                continue

    def retrieve_code_frequency(self, repo):
        print("- retrieving code frequency")
        code_frequency = repo.get_stats_code_frequency()

        # Create a dictionary to store the weekly aggregates
        churns = []

        # Extract the additions and deletions for each week
        for stats in code_frequency:
            additions = stats.additions
            deletions = stats.deletions
            churn = additions + deletions
            churns.append(churn)

        print("- finished retrieving pull request information")
        return churns


# def setup():
#     """Sets up external dependencies for the tool. For now, this is just environment loading."""
#     load_dotenv()
#
# setup()
# g = Github(os.environ.get("GITHUB_ACCESS_TOKEN1"))
# MetricsExtractor(g).extract()