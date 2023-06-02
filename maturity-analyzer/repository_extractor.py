import calendar
import json
import time
import datetime
from enum import Enum

from github import RateLimitExceededException


class MaturityLevel(Enum):
    MATURE = "mature", 10, 15, 6
    MIDDLE = "middle", 5, 10, 3
    IMMATURE = "immature", 0, 5, 1


class RepositoryExtractor:
    def __init__(self, github, num_repositories):
        self.github = github
        self.num_repositories = num_repositories
        self.ci_dir_filter = [".circleci", ".github", ".github/workflows"]

    def extract_repos(self):
        repos = {}
        for maturity_level in MaturityLevel:
            try:
                print("Retriving repositories for "+ maturity_level.value[0] + " projects")
                repo_list = self.extract_repos_per_maturity_group(maturity_level.value)
                repos[maturity_level.value[0]] = repo_list
                self.save_intermediate_results(repos)
            except RateLimitExceededException as e:
                print("Rate limit exceeded. Waiting for reset...")
                core_rate_limit = self.github.get_rate_limit().core
                reset_timestamp = calendar.timegm(core_rate_limit.reset.timetuple())
                sleep_time = reset_timestamp - calendar.timegm(time.gmtime())+ 5  # add 5 seconds to be sure the rate limit has been reset
                time.sleep(sleep_time)
                # Retry the extraction for the current maturity level
                repo_list = self.extract_repos_per_maturity_group(maturity_level.value)
                repos[maturity_level.value[0]] = repo_list
                self.save_intermediate_results(repos)

        return repos

    def extract_repos_per_maturity_group(self, maturity_level):
        age_lower_bound = maturity_level[1]
        age_upper_bound = maturity_level[2]

        age_lower_bound_years = (datetime.datetime.now() -
                                 datetime.timedelta(days=365 * age_lower_bound)).strftime("%Y-%m-%d")
        age_upper_bound_years = (datetime.datetime.now() -
                                 datetime.timedelta(days=365 * age_upper_bound)).strftime("%Y-%m-%d")
        max_last_updated = datetime.datetime.now() - datetime.timedelta(days=180)
        # Pagination variables
        page = 0
        repositories = []
        per_page = 100

        # Continuously extract repositories until you have at least 100 or reach the end of the search results
        while len(repositories) < self.num_repositories :
            try:
                # Search for repositories using the GitHub API
                results = self.github.search_repositories(
                    f'created:{age_upper_bound_years}..{age_lower_bound_years}',
                    'stars', 'desc')

                # Iterate over the search results
                for repo in results:
                    workflows = repo.get_workflows()
                    yml_files = self._extract_yml_files(repo)
                    # Check if the repository was last updated within the last 6 months
                    if repo.updated_at >= max_last_updated and (workflows.totalCount > 0 or yml_files):
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
            with open('repository_lists/repositories.json', 'r') as file:
                data = json.load(file)
                data.update(repos)
        except FileNotFoundError:
            data = repos

        with open('repository_lists/repositories.json', 'w') as file:
            json.dump(data, file)


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