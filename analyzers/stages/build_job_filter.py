import json
import os

from analyzers.stages.stage import PipelineStage


class BuildJobFilter(PipelineStage):
    def __init__(self, verbose=True):
        self.verbose = verbose
        self.total_jobs = 0
        self.build_jobs = 0

    def run(self, input):
        with open(os.path.join('output', 'workflow_runs_jobs.json'), 'r') as f:
            data = json.load(f)

        filtered_jobs = {}
        for repo_name, repo_data in data.items():
            if self.verbose:
                print(f'Processing repository: {repo_name}')
            for workflow in repo_data['workflows']:
                if 'runs' in workflow:
                    for run in workflow['runs']:
                        if 'jobs' in run:
                            for job in run['jobs']:
                                self.total_jobs += 1
                                if self.is_build_job(job):
                                    self.build_jobs += 1
                                    if repo_name not in filtered_jobs:
                                        filtered_jobs[repo_name] = {'workflows': []}
                                    workflow_copy = workflow.copy()  # So we don't alter the original data
                                    workflow_copy['runs'] = [run.copy()]  # Same here
                                    workflow_copy['runs'][0]['jobs'] = [job]  # Keep only the build job
                                    filtered_jobs[repo_name]['workflows'].append(workflow_copy)

        output_file_path = os.path.join('output', 'filtered_build_jobs.json')
        with open(output_file_path, 'w') as f:
            json.dump(filtered_jobs, f, indent=4)

        if self.verbose:
            print(f'Total jobs: {self.total_jobs}')
            print(f'Build jobs: {self.build_jobs}')
            print(f'Percentage of build jobs: {(self.build_jobs / self.total_jobs) * 100:.2f}%')

        return output_file_path

    def is_build_job(self, job):
        if 'build' in job['name'].lower():  # Check if this is a 'build' job
            return True
        if 'steps' in job:
            for step in job['steps']:
                if 'build' in step['name'].lower():
                    return True
        return False

