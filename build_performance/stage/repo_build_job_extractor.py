import os
import time
import requests
import concurrent.futures
import json

from build_performance.stage.stage import PipelineStage
from build_performance.utils import load_json_data


class RepoBuildJobExtractorConfig:
    def __init__(self, config):
        self.input_file = config["input_file"]
        self.output_file = config["output_file"]


class RepoBuildJobExtractor(PipelineStage):
    def __init__(self, github, args, config):
        self.verbose = args.verbose
        self.github = github
        self.config = RepoBuildJobExtractorConfig(config)
        self.token_index = 0
        self.tokens = [os.getenv(f'GITHUB_ACCESS_TOKEN{i}') for i in range(4)]  # load all tokens

    def run(self):
        data = load_json_data(self.config.input_file)
        with open(self.config.output_file, 'a') as outfile:
            for repo in data:
                print(f"Processing {repo['repoName']}")
                with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
                    for workflow in repo["workflow"]:
                        print(f"Processing {workflow['name']}")
                        # Create a new thread for each run to extract jobs
                        futures = {executor.submit(self.extract_jobs, repo["repoName"], run["id"]): run for run in
                                   workflow["runs_data"]}
                        for future in concurrent.futures.as_completed(futures):
                            run = futures[future]
                            try:
                                run["jobs"] = future.result()
                            except Exception as exc:
                                self.log_info(f'Generated an exception: {exc}')
                        print(f"Finished processing workflow for {repo['repoName']}")
                    # Save the modified data after processing each repo
                    outfile.write(json.dumps(repo, indent=4) + "\n")
                print(f"Finished processing {repo['repoName']}")

    def run(self):
        data = load_json_data(self.config.input_file)

        try:
            with open('processed_repos.txt', 'r') as processed_file:
                processed_repos = set(line.strip() for line in processed_file)
        except FileNotFoundError:
            processed_repos = set()

        with open(self.config.output_file, 'a') as outfile:
            for repo in data:
                # Skip repo if it's already been processed
                if repo['repoName'] in processed_repos:
                    continue
                print(f"Processing {repo['repoName']}")
                with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
                    for workflow in repo["workflow"]:
                        print(f"Processing {workflow['name']} with {len(workflow['runs_data'])} runs")
                        # Create a new thread for each run to extract jobs
                        futures = {executor.submit(self.extract_jobs, repo["repoName"], run["id"]): run for run in
                                   workflow["runs_data"]}
                        for future in concurrent.futures.as_completed(futures):
                            run = futures[future]
                            try:
                                run["jobs"] = future.result()
                            except Exception as exc:
                                self.log_info(f'Generated an exception: {exc}')
                        print(f"Finished processing workflow with name {workflow['name']} for {repo['repoName']}")
                    outfile.write(json.dumps(repo, indent=4) + "\n")

                print(f"Finished processing {repo['repoName']}")
                processed_repos.add(repo['repoName'])

                with open('processed_repos.txt', 'a') as processed_file:
                    processed_file.write(repo['repoName'] + '\n')

    def extract_jobs(self, repo_name, run_id):
        headers = {'Authorization': 'Token ' + self.tokens[self.token_index]}
        url = f"https://api.github.com/repos/{repo_name}/actions/runs/{run_id}/jobs"
        try:
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                if 'jobs' in response.json():
                    jobs = []
                    for job in response.json()['jobs']:
                        job_info = {
                            "id": job.get("id", ""),
                            "run_id": job.get("run_id", ""),
                            "status": job.get("status", ""),
                            "conclusion": job.get("conclusion", ""),
                            "started_at": job.get("started_at", ""),
                            "completed_at": job.get("completed_at", ""),
                            "name": job.get("name", ""),
                            "steps": job.get("steps", []),
                            "head_branch": job.get("head_branch", ""),
                        }
                        jobs.append(job_info)
                    return jobs
            elif response.status_code == 403:
                if 'X-RateLimit-Reset' in response.headers:
                    reset_time = int(response.headers['X-RateLimit-Reset'])
                    sleep_time = reset_time - time.time()
                    if sleep_time > 0:
                        self.log_info(f"Rate limit exceeded. Sleeping for {sleep_time} seconds.")
                        print(f"Switching to token {self.token_index + 1}")
                        self.token_index = (self.token_index + 1) % len(self.tokens)
                        headers = {'Authorization': 'Token ' + self.tokens[self.token_index]}

                        return self.extract_jobs(repo_name, run_id)
                else:
                    raise Exception(
                        f"403 Forbidden error for url: {url}. The request was understood but the server refuses to authorize it.")
            elif response.status_code == 404:
                self.log_info(f"Run not found for url: {url}. Skipping...")
                return []
            else:
                response.raise_for_status()
        except requests.exceptions.RequestException as e:
            self.log_info(f"RequestException: {e}")
            time.sleep(60)  # Wait for 60 seconds before retrying
            return self.extract_jobs(repo_name, run_id)
