import json

from analyzers.pipeline.stage import PipelineStage


class RepoWorkflowBuildFilterConfig:
    def __init__(self, config):
        self.input_file = config["input_file"]
        self.output_file = config["output_file"]
        self.keywords = config["keywords"]
        self.max_workflows = config["max_workflows"]
        self.min_runs = config["min_runs"]


class RepoWorkflowBuildFilter(PipelineStage):
    def __init__(self, args, config: RepoWorkflowBuildFilterConfig):
        self.verbose = args.verbose
        self.config = config
        self.filtered_workflows = 0
        self.filtered_runs = 0
        self.filtered_repos = 0

    def run(self):
        print('Filtering workflows...')
        data = self._load_data()

        # Using a copy of keys because we can't remove items from a dictionary during iteration
        for repo_name in list(data.keys()):
            data[repo_name]['workflows'] = [
                workflow for workflow in data[repo_name]['workflows']
                if self.filter_workflow(workflow)
            ]

            # If a repository has no workflows left, remove it
            if len(data[repo_name]['workflows']) == 0:
                del data[repo_name]
                self.filtered_repos += 1

            else:
                self.filtered_workflows += len(data[repo_name]['workflows'])

        self._save_filtered_data(data)

        print(f'Filtered out {self.filtered_workflows} workflows')
        print(f'Filtered out {self.filtered_repos} repositories')

    def _load_data(self):
        with open(self.config.input_file) as f:
            data = json.load(f)
        return data

    def _save_filtered_data(self, filtered_data):
        with open(self.config.output_file, 'w') as f:
            json.dump(filtered_data, f, indent=4)

    def filter_workflow(self, workflow):
        # Iterate over workflow's runs
        workflow['runs'] = [
            run for run in workflow['runs']
            if self.filter_run(run)
        ]

        self.filtered_runs += len(workflow['runs'])

        # Return False if all runs are filtered out
        return len(workflow['runs']) > 0

    def filter_run(self, run):
        # If jobs exist in the run, filter them
        if run.get('jobs') is not None:
            run['jobs'] = [
                job for job in run['jobs']
                if self.filter_job(job)
            ]
        # If no jobs or jobs is None, make it an empty list
        else:
            run['jobs'] = []

        # Return False if all jobs are filtered out or there are no jobs
        return len(run.get('jobs', [])) > 0

    def filter_job(self, job):
        # Check job's name and steps
        for keyword in self.config.keywords:
            if keyword.lower() in job['name'].lower():
                return True
            for step in job['steps']:
                if keyword.lower() in step['name'].lower():
                    return True

        # If neither job's name nor any step's name contains keyword, filter out the job
        return False
