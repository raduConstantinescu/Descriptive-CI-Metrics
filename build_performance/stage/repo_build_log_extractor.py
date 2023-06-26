import os
import time
import concurrent.futures
import math
from threading import Thread, Lock
import github
from build_performance.stage.stage import PipelineStage
from build_performance.utils import load_json_data, output_json_data


class RepoBuildLogExtractorConfig:
    def __init__(self, config):
        self.input_file = config["input_file"]
        self.output_file = config["output_file"]
        self.nr_of_builds = config["nr_of_builds"]


class RepoBuildLogExtractor(PipelineStage):
    def __init__(self, github, args, config):
        self.verbose = args.verbose
        self.github = github
        self.config = RepoBuildLogExtractorConfig(config)
        self.lock = Lock()  # a lock for synchronizing threads
        self.results = []  # a shared list to collect processed data
        self.github_tokens = ["GITHUB_TOKEN0", "GITHUB_TOKEN1", "GITHUB_TOKEN2", "GITHUB_TOKEN3"]
        self.current_token_index = 0

    def switch_token(self):
        self.current_token_index = (self.current_token_index + 1) % len(self.github_tokens)
        os.environ["GITHUB_TOKEN"] = os.environ.get(self.github_tokens[self.current_token_index])

    def run(self):
        print("Running RepoBuildLogExtractor")
        data = load_json_data(self.config.input_file)

        with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:  # Limit to 10 threads
            futures = []
            for repo_info in data:
                futures.append(executor.submit(self.download_build_runs, repo_info))

            # Wait for all threads to finish
            for future in concurrent.futures.as_completed(futures):
                try:
                    future.result()
                except Exception as e:
                    print(f"Thread resulted in an exception: {e}")

        output_json_data(self.config.output_file, self.results)

    def download_build_runs(self, repo_info):
        try:
            repo_name = repo_info["repoName"]
            if self.is_already_processed(repo_name):
                print(f"Skipping {repo_name} due to being already processed")
                return
            repo = self.github.get_repo(repo_name)
            if self.verbose:
                print(f"Downloading build logs for {repo_name}")
            self.download_build_runs_for_repo(repo, repo_info)
            self.save_to_processed_list(repo_name)
        except github.GithubException as e:
            if e.status == 403:
                # Check if it's a secondary rate limit error
                print(e.data['message'])
                if 'secondary' in e.data['message'].lower():
                    time.sleep(1)  # Sleep for a bit before retrying
                    self.download_build_runs(repo_info)
                else:
                    # Switch to next GitHub token
                    self.switch_token()
                    self.github = github.Github(os.environ.get("GITHUB_TOKEN"))
                    self.download_build_runs(repo_info)
            elif e.status == 502:
                print(f"Skipping due to server error for repo {repo_name}")
        except Exception as e:
            print(f"Error: {e}")

        with self.lock:
            self.results.append(repo_info)

    def download_build_runs_for_repo(self, repo, repo_info):
        for workflow_data in repo_info["workflow"]:
            workflow_id = workflow_data["id"]
            total_runs = workflow_data["runs"]
            target_runs = min(math.ceil(total_runs / 4), self.config.nr_of_builds)
            print(f"Decided to download {target_runs} runs out of {total_runs} ({(target_runs / total_runs) * 100}% for {repo.full_name} and with workflow name {workflow_data['name']})")

            # Retrieve the GitHub Workflow object using the workflow ID
            workflow = repo.get_workflow(workflow_id)
            workflow_runs = self.download_workflow_runs(workflow, target_runs)
            print(f"Downloaded {len(workflow_runs)} runs for {repo.full_name} and with workflow name {workflow_data['name']}")
            # Append the runs to the workflow_data dictionary
            workflow_data['runs_data'] = workflow_runs

    def download_workflow_runs(self, workflow, target_runs):
        runs = []
        for run in workflow.get_runs():
            if len(runs) >= target_runs:
                break
            run_info = {}
            run_info["id"] = run.id
            run_info["status"] = run.status
            run_info["conclusion"] = run.conclusion
            run_info['created_at'] = run.created_at.isoformat() if run.created_at else None
            run_info['updated_at'] = run.updated_at.isoformat() if run.updated_at else None
            run_info['head_branch'] = run.head_branch
            run_info['run_number'] = run.run_number
            run_info['run_attempt'] = run.run_attempt

            runs.append(run_info)
        return runs

    def is_already_processed(self, repo_name):
        with open("./output/repos_with_runs_data.txt", 'r') as file:
            for line in file:
                if line.strip() == repo_name:
                    return True
        return False

    def save_to_processed_list(self, repo):
        with open("./output/repos_with_runs_data.txt", 'a') as file:
            file.write(repo + '\n')

