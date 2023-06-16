import calendar
import time
import datetime

from github import RateLimitExceededException, GithubException, UnknownObjectException
from utils import load_repos, was_repo_processed, save_processed, save_filtered


class RepositoryFilter:
    def __init__(self, github):
        self.g = github
        self.repos = load_repos("./new_outputs/repos.txt")
        self.ci_dir_filter = [".jenkins",  ".travis.yml",  ".travis",  ".circleci/config.yml",  ".circleci",  ".github/workflows",  ".github",  "bitbucket-pipelines.yml",  "bitbucket-pipelines",  "azure-pipelines.yml",  ".azure-pipelines",  ".teamcity"]


    def filter(self):
        runs = 0
        for repo_name in self.repos:
            runs += 1
            print("Checking repository: " + repo_name)
            if was_repo_processed(repo_name, './new_outputs/filtered_names.txt'):
                print("Repo was already checked")
                continue
            while True:
                try:
                    repo = self.g.get_repo(repo_name)
                    constant_commits = self.has_constant_commit_stream(repo)
                    if constant_commits == 1:
                        file_count = self.count_repository_files(repo)
                        if file_count:
                            if self.extract_yml_files(repo) or repo.get_workflows().totalCount>0:
                                print(repo_name + " satisfies the conditions")
                                save_filtered(repo_name, True, './new_outputs/filtered_repos.json')
                            else:
                                save_filtered(repo_name, False, './new_outputs/filtered_repos.json')
                        else:
                            save_filtered(repo_name, False, './new_outputs/filtered_repos.json')
                    elif constant_commits == 0:
                        save_filtered(repo_name, False, './new_outputs/filtered_repos.json')
                    elif constant_commits == -1:
                        print("Repo has no content so skipping")
                    save_processed(repo_name, './new_outputs/filtered_names.txt')
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
                except UnknownObjectException:
                    print("Repository not found.")
                    exit()
                except GithubException as e:
                    if e.status == 409:
                        if "Git Repository is empty." in e.data['message']:
                            print("Repo is empty so skipping")
                            break
                        else:
                            print(e.data['message'])
                            print("Conflict occurred. Moving on...")
                    else:
                        print("An error occurred:", e)
                        exit()

        print(runs)


    def has_constant_commit_stream(self, repo):
        print(" - Checking constant number of commits")
        # Calculate the date 6 months ago
        six_months_ago = datetime.datetime.now() - datetime.timedelta(days=180)
        # Get all the commits in the repository
        commits = repo.get_commits()
        if commits.totalCount <= 100:
            return -1
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
            print(" - No days with commits")
            return 0
        # Calculate the commit frequency
        commit_frequency = commit_count / days_with_commits
        # Check if the commit stream is constant
        if commit_frequency >= 1:
            print(" - Commit frquency is good")
            return 1
        else:
            print(" - Commit frquency is bad")
            return 0

    def count_repository_files(self, repo):
        print("Counting the number of files")
        # Initialize the file count
        file_count = 0

        # Recursively count the number of files in the repository
        contents = repo.get_contents("")  # Get the root directory contents
        while contents and file_count < 500:
            file_content = contents.pop(0)
            if file_content.type == "file":
                file_count += 1
                if file_count >= 500:
                    break
            elif file_content.type == "dir":
                dir_contents = repo.get_contents(file_content.path)
                contents.extend(dir_contents)

        print("Number of files:", file_count)
        if file_count >= 500:
            return True
        else:
            return False

    def extract_yml_files(self, repo):
        print("Retrieving yml files")
        contents = repo.get_contents("")
        yml_files = []
        while contents:
            file_content = contents.pop(0)
            if file_content.type == "dir" and file_content.name in self.ci_dir_filter:
                contents.extend(repo.get_contents(file_content.path))
            else:
                if file_content.path == ".github/workflows":
                    contents.extend(repo.get_contents(file_content.path))
                if file_content.path.endswith(".yml") or file_content.path.endswith(".yaml"):
                    yml_files.append(file_content)

        print(f"Has {len(yml_files)} yml files")
        return yml_files

    # def save_repos(self, repo):
    #     with open("./output/filtered_repos.txt", 'a') as file:
    #             file.write(repo + '\n')
    #
    # def save_checked(self, repo):
    #     with open("./output/checked.txt", 'a') as file:
    #         file.write(repo + '\n')
    #
    # def is_repo_checked(self, repo_name):
    #     with open("./output/checked.txt", 'r') as file:
    #         for line in file:
    #             if line.strip() == repo_name:
    #                 return True
    #     return False
