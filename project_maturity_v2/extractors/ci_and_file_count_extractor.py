import calendar
import time
from github import RateLimitExceededException

from project_maturity_v2.utils import load_repos, save_data, save_processed, was_repo_processed


class RepoFileAnalyzer():
    def __init__(self, github):
        self.g = github
        self.repos = load_repos('../outputs_v2/repos.txt')
        self.ci_dir_filter = [".jenkins",  ".travis.yml",  ".travis",  ".circleci/config.yml",  ".circleci",  ".github/workflows",  ".github",  "bitbucket-pipelines.yml",  "bitbucket-pipelines",  "azure-pipelines.yml",  ".azure-pipelines",  ".teamcity"]


    def count_files(self):
        for repo_name in self.repos:
            print(f"Extracting files for repo {repo_name}")
            if was_repo_processed(repo_name, '../outputs_v2/processed_files_repos.txt'):
                print(f" - The repo was already processed")
                continue
            self.extract_files_information(repo_name)

    def extract_files_information(self, repo_name):
        while True:
            try:
                repo = self.g.get_repo(repo_name)
                files_count = self.count_repository_files(repo)
                yml_files = self.extract_yml_files(repo)
                value = {"files_count": files_count, "ci_files": yml_files}
                print(f" - Saving repo data")
                save_data(repo_name, value, '../outputs_v2/file_count.json')
                print("Adding repo to processed list")
                save_processed(repo_name, '../outputs_v2/processed_files_repos.txt')
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

    def count_repository_files(self, repo):
        print(" - Counting the number of files")
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

        print(f" - Repo has {file_count} files")
        return file_count


    def extract_yml_files(self, repo):
        print(" - Retrieving yml files")
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

        print(f" - Has {len(yml_files)} yml files")
        return len(yml_files)
