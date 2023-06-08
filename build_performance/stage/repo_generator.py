# This stage generates repositories based on the following criteria:
# 1. The repository must have at least min_stars stars.
# 2. The repository must be at least min_days_old days old.
# 3. The repository must contain one of the languages specified in the config.
# 4. For each language, the script must extract repo_number repositories.
# 5. The repositories must not be in the exclude_repos_file (used to exclude repositories that have already been processed).

import time
from datetime import datetime, timedelta

from github import GithubException

from build_performance.stage.stage import PipelineStage
from build_performance.utils import load_lines_from_file

class RepoGeneratorConfig:
    def __init__(self, config):
        self.languages = config["languages"]
        self.min_stars = config["min_stars"]
        self.repo_number = config["repo_number"]
        self.min_days_old = config["min_days_old"]
        self.output_file = config["output_file"]
        self.exclude_repos_file = config["exclude_repos_file"]

class RepoGenerator(PipelineStage):
    def __init__(self, github, args, config):
        self.g = github
        self.config = RepoGeneratorConfig(config)
        self.verbose = args.verbose
        self.excluded_repos = []

    def run(self):
        all_repos = []

        for language in self.config.languages:
            self.log_info(f"Searching repositories for language: {language}")
            repos = self._search_repos(language)
            all_repos.extend(repos)

        self.log_info(f"Writing {len(all_repos)} repositories to file...")
        self._write_repos(all_repos)
        self.log_info("Finished writing repositories.")

    def _search_repos(self, language):
        min_time = (datetime.now() - timedelta(days=self.config.min_days_old)).strftime('%Y-%m-%d')
        query = f'language:{language} stars:>={self.config.min_stars} created:<{min_time}'
        self.log_info(f"Executing search with query: {query}")

        random_repos = []
        self.log_info(f"Loading excluded repositories from file: {self.config.exclude_repos_file}")
        self.excluded_repos = load_lines_from_file(self.config.exclude_repos_file)

        while True:
            try:
                repos = self.g.search_repositories(query=query, sort='stars', order='desc')
                for repo in repos:
                    if repo.full_name in self.excluded_repos:
                        continue
                    random_repos.append(repo.full_name)
                    if len(random_repos) == self.config.repo_number:
                        break
                    time.sleep(0.05)
            except GithubException.RateLimitExceededException:
                self.log_info("Rate limit exceeded. Waiting for a sec...")
                time.sleep(2)  # Sleep 1 second
                continue

            self.log_info(f"Found {len(random_repos)} repositories for language {language}.")
            return random_repos

    def _write_repos(self, random_repos):
        with open(self.config.output_file, 'a') as file:
            for repo in random_repos:
                file.write(repo + '\n')