import concurrent.futures
import time
from itertools import dropwhile

import requests
import os
import json
from analyzers.pipeline.stage import PipelineStage


class JobExtractor(PipelineStage):
    def __init__(self, github, args):
        self.github = github
        self.verbose = args.verbose
        self.start = args.start

    def log_info(self, message):
        if self.verbose:
            print(message)

    def get_jobs(self, repo_name, run_id):
        headers = {'Authorization': 'Token ' + os.getenv('GITHUB_ACCESS_TOKEN')}
        url = f"https://api.github.com/repos/{repo_name}/actions/runs/{run_id}/jobs"
        try:
            response = requests.get(url, headers=headers)

            if response.status_code == 200:
                if 'jobs' in response.json():
                    jobs = []
                    for job in response.json()['jobs']:
                        job_info = {
                            "id": job.get("id", ""),
                            "status": job.get("status", ""),
                            "conclusion": job.get("conclusion", ""),
                            "started_at": job.get("started_at", ""),
                            "completed_at": job.get("completed_at", ""),
                            "name": job.get("name", ""),
                            "steps": job.get("steps", [])
                        }
                        jobs.append(job_info)
                    return jobs
            elif response.status_code == 403:
                if 'X-RateLimit-Reset' in response.headers:
                    reset_time = int(response.headers['X-RateLimit-Reset'])
                    sleep_time = reset_time - time.time()
                    if sleep_time > 0:
                        self.log_info(f"Rate limit exceeded. Sleeping for {sleep_time} seconds.")
                        time.sleep(sleep_time)
                        return self.get_jobs(repo_name, run_id)
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
            return self.get_jobs(repo_name, run_id)

    def run(self):

        # Load repo details from file
        output_dir = os.path.join('new_output')
        with open(os.path.join(output_dir, 'repo_metrics.json'), 'r') as f:
            repo_details = json.load(f)

        # Initialize a new dict to store intermediate results
        intermediate_results = {}

        # Convert repo_details from a list to an iterable of (index, repo)
        indexed_repos = enumerate(repo_details)

        # Skip to the desired start index if provided
        if self.start is not None:
            indexed_repos = dropwhile(lambda pair: pair[0] < self.start, indexed_repos)

        # Loop over repos
        for i, repo in indexed_repos:
            for repo_name, repo_data in repo.items():
                self.log_info(f"Processing repo {i}: {repo_name}")

                # Loop over workflows and their runs
                for workflow in repo_data['workflows']:
                    for run in workflow['runs']:
                        run_id = run['id']
                        self.log_info(f"Processing run: {run_id}")

                        max_attempts = 2
                        delay = 10
                        for attempt in range(max_attempts):
                            try:
                                # Create a thread for each run
                                with concurrent.futures.ThreadPoolExecutor() as executor:
                                    future = executor.submit(self.get_jobs, repo_name, run_id)

                                    # Save the result in the run
                                    run['jobs'] = future.result()
                                break  # If successful, move on to the next run
                            except requests.exceptions.HTTPError as e:
                                if e.response.status_code == 404:
                                    self.log_info(
                                        f"HTTP Error 404: Not Found for url: {e.request.url}. Skipping after {attempt + 1} attempts.")
                                    break
                                else:
                                    raise e  # If it's not a 404 error, then re-raise the exception
                            except Exception as e:
                                self.log_info(f"Error: {e}, Retrying in {delay} seconds...")
                                time.sleep(delay)
                                delay *= 2  # Increase the delay

                # Save intermediate results after processing each repo
                intermediate_results[repo_name] = repo_data
                with open(os.path.join(output_dir, 'intermediate_results.json'), 'w') as f:
                    json.dump(intermediate_results, f, default=str, indent=4)



