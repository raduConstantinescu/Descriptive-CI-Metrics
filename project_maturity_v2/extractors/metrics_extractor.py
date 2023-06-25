import calendar
import time

from github import RateLimitExceededException, GithubException

from project_maturity_v2.utils import was_repo_processed, save_data, save_processed, load_repos


class MetricsExtractor:
    def __init__(self, github):
        self.g = github
        self.repos = load_repos('outputs_v2/repos.txt')

    def extract(self):
        for repo_name in self.repos:
            if was_repo_processed(repo_name, "outputs_v2/processed_text_files/processed_repos.txt"):
                print(repo_name + " was already processed")
                continue
            self.extract_metrics(repo_name)

    def extract_metrics(self, repo_name):
        print("Extracting metrics for: " + repo_name)
        while True:
            try:
                repo = self.g.get_repo(repo_name)
                additions, deletions, churns = self.retrieve_code_frequency(repo)
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
                    "open_pull_requests_count": repo.get_pulls().totalCount,
                    "all_pull_requests_count": repo.get_pulls(state="all").totalCount,
                    "weekly_code_frequency": churns,
                    "weekly_code_additions": additions,
                    "weekly_code_deletions": deletions,
                    "weekly_commit_count_last_year": repo.get_stats_participation().all
                }
                print("- saving data")
                save_data(repo_name, metrics, 'outputs_v2/repo_data.json')
                print("- adding repo to processed repo file")
                save_processed(repo_name, "outputs_v2/processed_text_files/processed_repos.txt")
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
            except GithubException as e:
                if e.status == 403 and "The history or contributor list is too large to list contributors for this repository via the API." in e.headers['message']:
                    print(e)
                    break

    def retrieve_code_frequency(self, repo):
        print("- retrieving code frequency")
        code_frequency = repo.get_stats_code_frequency()

        # Create a dictionary to store the weekly aggregates
        additions_list = []
        deletions_list = []
        churns = []

        # Extract the additions and deletions for each week
        for stats in code_frequency:
            additions = stats.additions
            additions_list.append(additions)
            deletions = stats.deletions
            deletions_list.append(deletions)
            churn = additions + deletions
            churns.append(churn)

        print("- finished retrieving pull request information")
        return additions_list, deletions_list, churns
