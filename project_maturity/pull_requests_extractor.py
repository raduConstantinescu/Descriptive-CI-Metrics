import calendar
import datetime
import time

from github import RateLimitExceededException

from utils import load_repos, was_repo_processed, save_data, save_processed


class PullRequestsExtractor:
    def __init__(self, github):
        self.g = github
        self.repos = load_repos("./output/filtered_repos.txt")

    def extract(self):
        for repo_name in self.repos:
            print("Extracting information for: " + repo_name)
            if was_repo_processed(repo_name, "./output/processed_pr_repos.txt"):
                print(repo_name + " was already processed_pr_repos.txt")
                continue
            self.extract_pr_information(repo_name)
            save_processed(repo_name, './output/processed_pr_repos.txt')

    def extract_pr_information(self, repo_name):
        while True:
            try:
                repo = self.g.get_repo(repo_name)
                pr_information_data = self.retrieve_pull_request_information(repo)
                save_data(repo_name, pr_information_data, './output/pull_request_data.json')
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
        print("- retrieving pull request information")
        pull_requests = repo.get_pulls(state='all')
        six_months_ago = datetime.datetime.now() - datetime.timedelta(days=180)
        pr_data = []
        pr_count = 0

        for pr in pull_requests:
            if pr.created_at >= six_months_ago:
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
                pr_count += 1

                if pr_count >= 500:
                    break
        print(f"Extracted {pr_count} pull requests")
        print("Finished retrieving pull request information")
        return pr_data
