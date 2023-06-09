import calendar
import json
import os
import time
from datetime import datetime, timedelta, date

from github import RateLimitExceededException


class MetricsExtractor:
    def __init__(self, github):
        self.g = github
        self.repos = self.load_repos()

    def extract(self):
        for repo_name in self.repos:
            if self.was_repo_processed(repo_name):
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
                    "pull_requests": self.retrieve_pull_request_information(repo)
                }
                print("- saving data")
                self.save_repo_data(repo_name, metrics)
                print("- adding repo to processed")
                self.save_processed(repo_name)
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

    def retrieve_pull_request_information(self, repo):
        print("- retriving pull request information")
        pull_requests = repo.get_pulls()
        pr_data = []
        for pr in pull_requests:
            data = {
                "title": pr.title,
                "churn": pr.additions + pr.deletions,
                "changed_files_count": pr.changed_files,
                "commit_count": pr.commits,
                "created_at": pr.created_at.isoformat(),
                "merged": pr.merged
            }
            if pr.closed_at is not None:
                data["closed_at"] = pr.closed_at.isoformat()
            else:
                data["closed_at"] = None
            if pr.merged_at is not None:
                data["merged_at"] = pr.merged_at.isoformat()
            else:
                data["merged_at"] = None
            pr_data.append(data)
        print("- saving pull request information")
        self.save_pr_data(repo.full_name, pr_data)
        print("finished retrieving pull request information")
        return(pull_requests.totalCount)


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


    def load_repos(self):
        repo_list = []
        with open("./output/filtered_repos.txt", 'r') as file:
            for line in file:
                # Remove leading/trailing whitespace and newline characters
                repo_name = line.strip()
                repo_list.append(repo_name)
        return repo_list

    def save_repo_data(self, key, value):
        data = {}

        if os.path.exists('./output/repo_data.json') and os.path.getsize('./output/repo_data.json') > 0:
            with open('./output/repo_data.json', 'r') as file:
                data = json.load(file)  # Load existing JSON data

        if 'code_frequency' in value:
            value['code_frequency'] = json.dumps(value['code_frequency'])

        data[key] = value  # Add the new key-value pair

        with open('./output/repo_data.json', 'w') as file:
            json.dump(data, file, indent=4)  # Write updated data back to the JSON file

    def save_pr_data(self, key, value):
        data = {}

        if os.path.exists('./output/pull_request_data.json') and os.path.getsize('./output/pull_request_data.json') > 0:
            with open('./output/pull_request_data.json', 'r') as file:
                data = json.load(file)  # Load existing JSON data

        data[key] = value  # Add the new key-value pair

        with open('./output/pull_request_data.json', 'w') as file:
            json.dump(data, file, indent=4)  # Write updated data back to the JSON file

    def save_processed(self, repo):
        with open("./output/processed_repos.txt", 'a') as file:
            file.write(repo + '\n')

    def was_repo_processed(self, repo_name):
        with open("./output/processed_repos.txt", 'r') as file:
            for line in file:
                if line.strip() == repo_name:
                    return True
        return False

