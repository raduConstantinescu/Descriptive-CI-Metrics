from datetime import datetime, timedelta
from analyzers.pipeline.stage import PipelineStage

# TODO: number of repos per language
class RepoGenerator(PipelineStage):
    def __init__(self, github, args, config):
        self.g = github
        self.config = config
        self.verbose = args.verbose
        self.excluded_repos = self._load_excluded_repos()

    def run(self):
        all_repos = []

        for language in self.config.languages:
            self.log_info(f"Searching repositories for language: {language}")
            repos = self._search_repos(language)
            all_repos.extend(repos)

        self.log_info(f"Writing {len(all_repos)} repositories to file...")
        self._write_repos(all_repos)
        self.log_info("Finished writing repositories.")

    def _load_excluded_repos(self):
        self.log_info("Loading excluded repositories...")
        excluded_repos = []
        with open(self.config.exclude_repos_file, 'r') as file:
            for line in file:
                excluded_repos.append(line.strip())
        return excluded_repos

    def _write_repos(self, random_repos):
        with open(self.config.output_file, 'a') as file:
            for repo in random_repos:
                file.write(repo + '\n')

    def _search_repos(self, language):
        min_time = (datetime.now() - timedelta(days=self.config.min_days_old)).strftime('%Y-%m-%d')
        query = f'language:{language} stars:>={self.config.min_stars} created:<{min_time}'
        self.log_info(f"Executing search with query: {query}")
        repos = self.g.search_repositories(query=query, sort='stars', order='desc')

        random_repos = []
        for repo in repos:
            if repo.full_name in self.excluded_repos:
                continue
            random_repos.append(repo.full_name)
            if len(random_repos) == 10:
                break

        self.log_info(f"Found {len(random_repos)} repositories for language {language}.")
        return random_repos

    # This is a helper method to print messages to the console if the verbose flag is set
    def log_info(self, message):
        if self.verbose:
            print(message)

class RepoGeneratorConfig:
    def __init__(self, config):
        self.languages = config["languages"]
        self.min_stars = config["min_stars"]
        self.min_days_old = config["min_days_old"]
        self.output_file = config["output_file"]
        self.exclude_repos_file = config["exclude_repos_file"]
