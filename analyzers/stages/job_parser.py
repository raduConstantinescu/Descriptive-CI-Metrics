import requests
import os
import json
from github import Github

from analyzers.stages.stage import PipelineStage

class JobParser(PipelineStage):
    def __init__(self, verbose=True):
        self.g = Github(os.getenv('GITHUB_ACCESS_TOKEN'))
        self.verbose = verbose

    def run(self, input):
        with open(os.path.join('output', 'workflow_runs.json'), 'r') as f:
            data = json.load(f)

        results = {}
        for repo_name, repo_data in data.items():
            if self.verbose:
                print(f'Processing repository: {repo_name}')
            for workflow in repo_data['workflows']:
                if self.verbose:
                    print(f'Processing workflow: {workflow["name"]}')
                if 'runs' in workflow:
                    for run in workflow['runs']:
                        try:
                            if self.verbose:
                                print(f'Processing run: {run["id"]}')
                            jobs = self.get_jobs(repo_name, run['id'])
                            run['jobs'] = jobs
                        except Exception as e:
                            print(f"Failed to fetch jobs for run {run['id']} in workflow {workflow['id']} in repository {repo_name}. Error: {e}")
            results[repo_name] = repo_data

        output_path = os.path.join('output', 'workflow_runs_jobs.json')
        with open(output_path, 'w') as f:
            json.dump(results, f, indent=4)

        return output_path

    def get_jobs(self, repo_name, run_id):
        headers = {'Authorization': 'Token ' + os.getenv('GITHUB_ACCESS_TOKEN')}
        url = f"https://api.github.com/repos/{repo_name}/actions/runs/{run_id}/jobs"
        response = requests.get(url, headers=headers)
        return response.json()['jobs']
