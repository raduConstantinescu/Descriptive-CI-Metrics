import calendar
import json
import time
import datetime
from enum import Enum

from github import RateLimitExceededException

class RepositoryFilter:
    def __init__(self, github):
        self.g = github
        self.repos = self.load_repos()

    def filter(self):
        filtered_repos = []
        runs = 0
        for repo_name in self.repos:
            runs += 1
            print("Checking repository: " + repo_name)
            if self.is_repo_checked(repo_name):
                print("Repo was already checked")
                continue
            self.save_checked(repo_name)
            while True:
                try:
                    repo = self.g.get_repo(repo_name)
                    constant_commits = self.has_constant_commit_stream(repo)
                    if constant_commits:
                        file_count = self.count_repository_files(repo)
                        if file_count:
                            print(repo_name + " satisfies the conditions")
                            self.save_repos(repo_name)
                            filtered_repos.append(repo_name)
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

        print(runs)
        # self.save_repos(filtered_repos)


    # def filter_repos(self):
    #
    # def save_results(self, repos):

    def load_repos(self):
        repo_list = []
        with open("./output/repos.txt", 'r') as file:
            for line in file:
                # Remove leading/trailing whitespace and newline characters
                repo_name = line.strip()
                repo_list.append(repo_name)
        return repo_list

    def has_constant_commit_stream(self, repo):
        print("Checking constant number of commits")
        # Calculate the date 6 months ago
        six_months_ago = datetime.datetime.now() - datetime.timedelta(days=180)

        # Get all the commits in the repository
        commits = repo.get_commits()

        # Count the number of commits and days with commits in the last 6 months
        commit_count = 0
        commit_dates = set()
        for commit in commits:
            commit_date = commit.commit.author.date
            if commit_date > six_months_ago:
                commit_count += 1
                commit_dates.add(commit_date.date())
            else:
                break  # Stop counting if a commit is older than 6 months

        # Calculate the number of days with commits
        days_with_commits = len(commit_dates)

        if days_with_commits == 0:
            return False

        # Calculate the commit frequency
        commit_frequency = commit_count / days_with_commits

        # Check if the commit stream is constant
        if commit_frequency >= 1:
            print("true")
            return True
        else:
            print("false")
            return False

    def count_repository_files(self, repo):
        print("Counting the number of files")
        # Initialize the file count
        file_count = 0

        # Recursively count the number of files in the repository
        contents = repo.get_contents("")  # Get the root directory contents
        while contents and file_count < 100:
            file_content = contents.pop(0)
            if file_content.type == "file":
                file_count += 1
                if file_count >= 100:
                    break
            elif file_content.type == "dir":
                dir_contents = repo.get_contents(file_content.path)
                contents.extend(dir_contents)

        print("Number of files:", file_count)
        if file_count >= 100:
            return True
        else:
            return False

    def save_repos(self, repo):
        with open("./output/filtered_repos.txt", 'a') as file:
                file.write(repo + '\n')

    def save_checked(self, repo):
        with open("./output/checked.txt", 'a') as file:
            file.write(repo + '\n')

    def is_repo_checked(self, repo_name):
        with open("./output/checked.txt", 'r') as file:
            for line in file:
                if line.strip() == repo_name:
                    return True
        return False
