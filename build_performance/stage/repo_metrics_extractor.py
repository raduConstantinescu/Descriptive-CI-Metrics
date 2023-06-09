# This file contains the RepoMetricsExtractor class, which is responsible for extracting metrics from the GitHub API
# We refer to these metrics at Project Level Metrics, as they are related to the repository as a whole
# The data extracted will be:
#   - Number of commits
#   - Number of branches
#   - Number of releases
#   - Number of contributors
#   - Number of stars
#   - Number of forks
#   - Size of repository in KB
#   - Creation date
#   - Primary programming language (must be one of the languages that have already been filtered on)

# We will save the output into a new JSON file with the same structure but with the appended data.
# We will also include threading as this can take a while...

from build_performance.stage.stage import PipelineStage
from build_performance.utils import load_json_data, output_json_data
import os
from github import RateLimitExceededException
from threading import Thread, Lock
import time
import calendar

class RepoMetricsExtractorConfig:
    def __init__(self, config):
        self.input_file = config["input_file"]
        self.output_file = config["output_file"]

class RepoMetricsExtractor(PipelineStage):
    def __init__(self, github, args, config):
        self.verbose = args.verbose
        self.github = github
        self.config = RepoMetricsExtractorConfig(config)
        self.lock = Lock()  # a lock for synchronizing threads
        self.processed_data = []  # a shared list to collect processed data

    def run(self):
        print("Running RepoMetricsExtractor")
        data = load_json_data(self.config.input_file)

        threads = []
        for repo in data:
            thread = Thread(target=self.extract_repo_metrics, args=(repo,))
            thread.start()
            threads.append(thread)

        for thread in threads:
            thread.join()

        output_dir = os.path.dirname(self.config.output_file)
        os.makedirs(output_dir, exist_ok=True)
        output_json_data(self.config.output_file, self.processed_data)

        print("Finished writing repository metrics.")

        # todo: add a option to not have to run whole stage
        # self.show_statistics(self.processed_data)

    def extract_repo_metrics(self, repo):
        while True:
            try:
                self.log_info(f"Extracting metrics for {repo['repoName']}")
                repo_obj = self.github.get_repo(repo["repoName"])
                repo["metrics"] = {
                    "language": repo_obj.language,
                    "commits": repo_obj.get_commits().totalCount,
                    "branches": repo_obj.get_branches().totalCount,
                    "releases": repo_obj.get_releases().totalCount,
                    "contributors": repo_obj.get_contributors().totalCount,
                    "stars": repo_obj.stargazers_count,
                    "forks": repo_obj.forks_count,
                    "size": repo_obj.size,
                    "created_at": repo_obj.created_at.isoformat()
                }

                with self.lock:
                    self.processed_data.append(repo)

                break
            except RateLimitExceededException:
                print("Rate limit exceeded. Waiting for reset...")
                core_rate_limit = self.github.get_rate_limit().core
                reset_timestamp = calendar.timegm(core_rate_limit.reset.timetuple())
                sleep_time = reset_timestamp - calendar.timegm(
                    time.gmtime()) + 5  # 5 seconds buffer time to be safe
                time.sleep(sleep_time)
                continue
            except Exception as e:
                print(f"Error extracting metrics for {repo['repoName']}: {e}")