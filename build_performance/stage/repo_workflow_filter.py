# This stage filters the repositories based on the following criteria:
# 1. The repository must have at least one workflow with more than 500 runs.
# 2. The repository must have at least one workflow with more than 500 runs and the workflow must have a directory

import concurrent
import os
import time
from concurrent.futures import ThreadPoolExecutor
from github import RateLimitExceededException
from build_performance.utils import load_lines_from_file, output_json_data
from build_performance.stage.stage import PipelineStage

class RepoWorkflowFiltering:
    def __init__(self, config):
        self.input_file = config["input_file"]
        self.ci_dir_filter = config["ci_dir_filter"]
        self.output_file = config["output_file"]

class RepoWorkflowFiltering(PipelineStage):
    def __init__(self, github, args, config):
        self.verbose = args.verbose
        self.github = github
        self.config = RepoFilteringConfig(config)

    def run(self):
        self.log_info(f"Loading repositories from file: {self.config.input_file}")
        repos = load_lines_from_file(self.config.input_file)
        filtered_repos = []

        with ThreadPoolExecutor(max_workers=5) as executor:
            future_to_repo = {executor.submit(self.filter_repo, repo_name): repo_name for repo_name in repos}
            for future in concurrent.futures.as_completed(future_to_repo):
                repo_name = future_to_repo[future]
                try:
                    filtered_repo = future.result()
                    if filtered_repo is not None:
                        filtered_repos.append(filtered_repo)
                except RateLimitExceededException as e:
                    self.log_info(
                        f"Remaining API calls before the request: {self.github.get_rate_limit().core.remaining}")
                    self.log_info(f"Time when rate limit will be reset: {self.github.get_rate_limit().core.reset}")

                    reset_time = self.github.get_rate_limit().core.reset.timestamp()  # get the reset time in timestamp format
                    sleep_time = reset_time - time.time()

                    if sleep_time > 0:
                        self.log_info(f"Rate limit exceeded. Sleeping for {sleep_time} seconds.")
                        time.sleep(sleep_time)

                except Exception as e:
                    self.log_info(f"Error while processing repo {repo_name}: {str(e)}")

        self.log_info(f"Writing {len(filtered_repos)} repositories to file...")

        output_dir = os.path.dirname(self.config.output_file)
        os.makedirs(output_dir, exist_ok=True)

        output_json_data(self.config.output_file, filtered_repos)
        self.log_info("Finished writing repositories.")

    def filter_repo(self, repo_name):
        repo = self.github.get_repo(repo_name)

        workflows = []
        for workflow in repo.get_workflows():
            if workflow.get_runs().totalCount >= 500:
                workflows.append({
                    "name": workflow.name,
                    "id": workflow.id
                })

        if workflows:
            return {
                "repoName": repo_name,
                "workflow": workflows
            }
