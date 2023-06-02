import calendar
import time
from datetime import datetime, timedelta

from github import RateLimitExceededException, Repository

from extractor.utils import log_info

class Generator:

    def __init__(self, args, g, config_data):
        self.verbose = args.verbose
        self.g = g
        self.config_data = config_data
        self.maturity_level = None
        self.language = None

    def run(self):
        repos = {}
        if self.config_data["RepoGenerator"]["maturity_filter"] == True:
            for maturity_level in self.config_data["MaturityLevel"].items():
                self.maturity_level = maturity_level
                repos[maturity_level[0]] = self.generate()
        if len(self.config_data["RepoGenerator"]["languages"]) != 0:
            for language in self.config_data["RepoGenerator"]["languages"]:
                self.language = language
                repos[language] = self.generate()
        log_info(self.verbose, repos)
        log_info(self.verbose, len(repos))
        return repos



    def generate(self):
        generator_config = self.config_data["RepoGenerator"]
        repos = []
        while len(repos) < generator_config["target_number_of_repos"]:
            try:
                response = self.g.search_repositories(self.generate_query_from_config(generator_config), 'stars', 'desc')

                for repo in response:
                    check = self.check_repo(repo, generator_config)
                    if check:
                        repos.append(repo)
                    if len(repos) >= generator_config["target_number_of_repos"]:
                        break

                if len(repos) >= generator_config["target_number_of_repos"]:
                    break

            except RateLimitExceededException as e:
                log_info(self.verbose, "Rate limit exceeded. Waiting for reset...")
                core_rate_limit = self.github.get_rate_limit().core
                reset_timestamp = calendar.timegm(core_rate_limit.reset.timetuple())
                sleep_time = reset_timestamp - calendar.timegm(
                    time.gmtime()) + 5  # add 5 seconds to be sure the rate limit has been reset
                time.sleep(sleep_time)
                # Retry the current search
                continue

        return repos

    def generate_query_from_config(self, generator_config):
        query = f'is:public template:false stars:>={generator_config["min_stars"]}'

        if self.maturity_level is None:
            min_time = (datetime.now() - timedelta(days=generator_config["min_days_old"])).strftime('%Y-%m-%d')
            query += f' created:<{min_time}'
        else:
            min_age = (datetime.now() - timedelta(days=365 * self.maturity_level[1]["minimum_age"])).strftime("%Y-%m-%d")
            max_age = (datetime.now() - timedelta(days=365 * self.maturity_level[1]["maximum_age"])).strftime("%Y-%m-%d")
            query += f' created:{max_age}..{min_age}'

        if self.language is not None:
            query += f' language:{self.language}'

        return query

    def check_repo(self, repo, generator_config) -> Repository:
        max_last_updated = datetime.now() - timedelta(days=generator_config["days_since_last_update"])
        if repo.archived is True or repo.fork is True or repo.updated_at < max_last_updated:
            return False

        # TODO: keywords for ci
        if repo.get_workflows().totalCount <= 0:
           return False

        if repo.get_commits().totalCount < generator_config["min_commits"]:
            return False

        if repo.get_contributors().totalCount < generator_config["min_contributors"]:
            return False

        return True