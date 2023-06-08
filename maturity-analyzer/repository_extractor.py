import calendar
import json
import time
import datetime
from enum import Enum

from github import RateLimitExceededException


class RepositoryExtractor:
    def __init__(self, github, num_repositories):
        self.github = github
        self.num_repositories = num_repositories
        self.ci_dir_filter = [".circleci", ".github", ".github/workflows"]

    def extract(self):
        repos = []
        try:
            print("Retriving repositories")
            repo_list = self.extract_repos()
            repos.extend(repo_list)
            self.save_intermediate_results(repos)
        except RateLimitExceededException as e:
            print("Rate limit exceeded. Waiting for reset...")
            core_rate_limit = self.github.get_rate_limit().core
            reset_timestamp = calendar.timegm(core_rate_limit.reset.timetuple())
            sleep_time = reset_timestamp - calendar.timegm(time.gmtime())+ 5  # add 5 seconds to be sure the rate limit has been reset
            time.sleep(sleep_time)
            # Retry the extraction for the current maturity level
            repo_list = self.extract_repos()
            repos.extend(repo_list)
            self.save_intermediate_results(repos)

        return repos

    def extract_repos(self):
        minimum_age = (datetime.datetime.now() - datetime.timedelta(days=365)).strftime('%Y-%m-%d')
        max_last_updated = datetime.datetime.now() - datetime.timedelta(days=180)
        # Pagination variables
        page = 0
        repositories = []

        # Continuously extract repositories until you have at least 100 or reach the end of the search results
        while len(repositories) < self.num_repositories :
            try:
                # Search for repositories using the GitHub API
                results = self.github.search_repositories(
                    f'created:<{minimum_age} is:public template:false stars:>=100 fork:false',
                    'stars', 'desc')

                # Iterate over the search results
                for repo in results:

                    workflows = repo.get_workflows()
                    yml_files = self._extract_yml_files(repo)
                    # Check if the repository was last updated within the last 6 months
                    if repo.updated_at >= max_last_updated and (workflows.totalCount > 0 or yml_files):
                        print("Adding repo: " + f'{repo.owner.login}/{repo.name}')
                        repositories.append({
                            'name': f'{repo.owner.login}/{repo.name}',
                            'created_at': repo.created_at.strftime("%Y-%m-%d"),
                            'updated_at': repo.updated_at.strftime("%Y-%m-%d"),
                            'stargazers_count': repo.stargazers_count,
                            'watchers_count': repo.watchers_count,
                            'forks_count': repo.forks_count
                        })
                        if len(repositories) >= self.num_repositories :
                            break

                if page >= results.totalCount or len(repositories) >= self.num_repositories :
                    break

                page += 1
            except RateLimitExceededException as e:
                print("Rate limit exceeded. Waiting for reset...")
                core_rate_limit = self.github.get_rate_limit().core
                reset_timestamp = calendar.timegm(core_rate_limit.reset.timetuple())
                sleep_time = reset_timestamp - calendar.timegm(
                    time.gmtime()) + 5  # add 5 seconds to be sure the rate limit has been reset
                time.sleep(sleep_time)
                # Retry the current search
                continue

        return repositories

    def save_intermediate_results(self, repos):
        try:
            with open('raw_repository_lists_sorted_by_last_updated/repositories.json', 'r+') as file:
                try:
                    data = json.load(file)
                except json.decoder.JSONDecodeError:
                    data = {}

                for repo in repos:
                    repo_name = repo['name']
                    data[repo_name] = repo

                file.seek(0)
                json.dump(data, file, indent=4)
                file.truncate()
        except FileNotFoundError:
            with open('raw_repository_lists_sorted_by_last_updated/repositories.json', 'w') as file:
                json.dump(repos, file, indent= 4)


    def _extract_yml_files(self, repo):
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
        return yml_files