import json
import os
import time
from github import GithubException, Github

from analyzers.stages.stage import PipelineStage


import time

class WorkflowRunsParser(PipelineStage):
    def __init__(self, verbose=True):
        self.g = Github(os.getenv('GITHUB_ACCESS_TOKEN'))
        self.verbose = verbose

    def run(self, input):
        with open(os.path.join('output', 'filtered_repos.json'), 'r') as f:
            data = json.load(f)

        results = {}
        for repo_name, repo_data in data.items():
            if self.verbose:
                print(f'Processing repository: {repo_name}')
            repo = self.g.get_repo(repo_name)
            for workflow in repo_data['workflows']:
                if self.verbose:
                    print(f'Processing workflow: {workflow["name"]}')
                start_time = time.time()
                try:
                    wf = repo.get_workflow(workflow['id'])
                    runs = wf.get_runs()
                    workflow['total_runs'] = runs.totalCount  # Add total run count

                    # Fetch the latest 1000 runs, if there are at least 1000, otherwise fetch all runs
                    num_runs_to_fetch = min(1000, workflow['total_runs'])

                    workflow_runs = []
                    page = 0
                    while len(workflow_runs) < num_runs_to_fetch:
                        runs_page = runs.get_page(page)
                        if not runs_page:
                            break
                        workflow_runs.extend(runs_page[:num_runs_to_fetch - len(workflow_runs)])
                        page += 1

                    for run in workflow_runs:
                        run_data = {
                            'id': run.id,
                            'head_sha': run.head_sha,
                            'run_number': run.run_number,
                            'status': run.status,
                            'conclusion': run.conclusion,
                            'created_at': run.created_at.isoformat(),
                            'updated_at': run.updated_at.isoformat(),
                            'execution_time': (run.updated_at - run.created_at).total_seconds(),
                        }
                        workflow['runs'].append(run_data)
                except GithubException as e:
                    print(f"Failed to fetch runs for workflow {workflow['id']} in repository {repo_name}. Error: {e}")
                end_time = time.time()
                if self.verbose:
                    print(
                        f'Finished processing workflow: {workflow["name"]}. Time taken: {end_time - start_time:.2f} seconds.')
            results[repo_name] = repo_data

        output_path = os.path.join('output', 'workflow_runs2.json')
        with open(output_path, 'w') as f:
            json.dump(results, f, indent=4)

        return output_path


