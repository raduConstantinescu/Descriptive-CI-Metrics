import github
from dateutil.parser import isoparse
from github import Github
from dotenv import load_dotenv
import matplotlib.pyplot as plt
from collections import defaultdict
import os
import re
import argparse
import requests
import json
import time


load_dotenv()


class PipelineStage:
    def run(self, input):
        raise NotImplementedError()

class RepoParser(PipelineStage):
    def __init__(self):
        self.g = Github(os.getenv('GITHUB_ACCESS_TOKEN'))

    def run(self, input):
        with open(os.path.join('..', input), 'r') as f:
            repos = f.read().splitlines()

        workflows = {}
        for repo in repos:
            repo_obj = self.g.get_repo(repo)
            workflows[repo] = self.get_workflows(repo_obj)

        os.makedirs('output', exist_ok=True)
        output_path = os.path.join('output', 'workflows.json')
        with open(output_path, 'w') as f:
            json.dump(workflows, f, indent=4)
        return output_path

    def get_workflows(self, repo):
        workflows = repo.get_workflows()
        result = []
        for wf in workflows:
            result.append({
                'id': wf.id,
                'name': wf.name,
            })
        return result


class WorkflowFilter(PipelineStage):
    def __init__(self, filter_fn=None):
        if filter_fn is None:
            self.filter_fn = self.is_ci_workflow
        else:
            self.filter_fn = filter_fn

    def run(self, input):
        with open(input, 'r') as f:
            workflows = json.load(f)

        filtered_workflows = {}
        for repo, wfs in workflows.items():
            filtered_workflows[repo] = list(filter(self.filter_fn, wfs))

        os.makedirs('output', exist_ok=True)
        output_path = os.path.join('output', 'filtered_workflows.json')
        with open(output_path, 'w') as f:
            json.dump(filtered_workflows, f, indent=4)
        return output_path

    @staticmethod
    def is_ci_workflow(workflow):
        ci_keywords = ["CI", "Continuous Integration", "Build", "Test", "Pipeline", "Deploy", "Release", "PR", "Lint"]
        pattern = re.compile("|".join(ci_keywords), re.IGNORECASE)
        return bool(pattern.search(workflow['name']))


class CIPlotter(PipelineStage):
    def run(self, input):
        with open(input, 'r') as f:
            analysis = json.load(f)

        os.makedirs('output', exist_ok=True)
        for repo, wfs in analysis.items():
            for wf in wfs:
                self.plot_workflow(repo, wf)
        return input  # This stage doesn't produce a new output file

    def plot_workflow(self, repo, wf):
        x = list(range(1, len(wf['analysis']) + 1))
        y = [run['execution_time'] for run in wf['analysis']]

        plt.figure()
        plt.plot(x, y)
        plt.xlabel('Run number')
        plt.ylabel('Execution time (s)')
        plt.title(f'{repo} - {wf["workflow"]["name"]}')
        plt.savefig(os.path.join('output', f'{repo.replace("/", "_")}_{wf["workflow"]["id"]}.png'))


class WorkflowAnalyser(PipelineStage):
    def __init__(self, verbose=False):
        self.g = Github(os.getenv('GITHUB_ACCESS_TOKEN'))
        self.verbose = verbose

    def run(self, input):
        with open(input, 'r') as f:
            workflows = json.load(f)

        analysis = {}
        for repo, wfs in workflows.items():
            if self.verbose:
                print(f"Processing repo: {repo}")
            analysis[repo] = [self.analyse_workflow(repo, wf) for wf in wfs]

        os.makedirs('output', exist_ok=True)
        output_path = os.path.join('output', 'analysis.json')
        with open(output_path, 'w') as f:
            json.dump(analysis, f, indent=4)
        return output_path

    def analyse_workflow(self, repo, workflow):
        if self.verbose:
            print(f"Analysing workflow: {workflow['name']} for repo: {repo}")
        repo_obj = self.g.get_repo(repo)
        wf_obj = repo_obj.get_workflow(workflow['id'])

        runs = self.get_workflow_runs_with_retry(repo_obj, wf_obj)
        result = []
        successful_runs = 0
        for run in runs[:10]:
            conclusion = run.conclusion
            if conclusion == 'success':
                successful_runs += 1
            result.append({
                'id' : run.id,
                'conclusion': conclusion,
                'execution_time': (run.updated_at - run.created_at).total_seconds(),
            })
        return {
            'workflow': workflow,
            'analysis': result,
            'success_rate': successful_runs / 10 if runs.totalCount >= 10 else successful_runs / runs.totalCount,
        }

    def get_workflow_runs_with_retry(self, repo_obj, wf_obj, retries=3, delay=5):
        for _ in range(retries):
            try:
                return wf_obj.get_runs()
            except github.GithubException as e:
                if e.status == 502:  # Server error
                    print("Server error, retrying...")
                    time.sleep(delay)  # Wait before retrying
                else:
                    raise  # Some other error occurred, re-raise the exception
        raise Exception("Failed to get workflow runs after multiple retries")

class JobFetcher(PipelineStage):
    def __init__(self, verbose=False):
        self.verbose = verbose

    def run(self, input):
        with open(input, 'r') as f:
            analysis = json.load(f)

        jobs_analysis = {}
        for repo, workflow_analyses in analysis.items():
            if self.verbose:
                print(f"Processing repo: {repo}")
            jobs_analysis[repo] = [self.fetch_jobs_for_workflow_analysis(repo, wf_analysis) for wf_analysis in workflow_analyses]

        os.makedirs('output', exist_ok=True)
        output_path = os.path.join('output', 'workflow_jobs.json')
        with open(output_path, 'w') as f:
            json.dump(jobs_analysis, f, indent=4)
        return output_path

    def fetch_jobs_for_workflow_analysis(self, repo, workflow_analysis):
        workflow = workflow_analysis['workflow']
        run_ids = [analysis['id'] for analysis in workflow_analysis['analysis']]

        try:
            if self.verbose:
                print(f"Fetching jobs for workflow: {workflow['name']} for repo: {repo}")
        except KeyError as e:
            print(f"KeyError: {str(e)}")
            print(f"Workflow: {workflow}")
            return {}

        headers = {'Authorization': f'token {os.getenv("GITHUB_ACCESS_TOKEN")}'}
        jobs = []
        for run_id in run_ids:
            url = f"https://api.github.com/repos/{repo}/actions/runs/{run_id}/jobs"
            response = requests.get(url, headers=headers)
            if response.status_code != 200:
                print(f"Failed to fetch jobs for run {run_id}: {response.status_code}")
                continue

            job_data = response.json()
            for job in job_data['jobs']:
                filtered_job = {
                    'id': job['id'],
                    'run_id': job['run_id'],
                    'workflow_name': workflow['name'],
                    'status': job['status'],
                    'conclusion': job['conclusion'],
                    'created_at': job['created_at'],
                    'started_at': job['started_at'],
                    'completed_at': job['completed_at'],
                    'name': job['name'],
                    'steps': job['steps']
                }
                jobs.append(filtered_job)

        return {
            'workflow': workflow,
            'analysis': workflow_analysis['analysis'],
            'jobs': jobs
        }

class BuildJobFilter(PipelineStage):
    def __init__(self, verbose=False):
        self.verbose = verbose

    def run(self, input):
        with open(input, 'r') as f:
            workflow_jobs = json.load(f)

        build_jobs = {}
        for repo, wfs in workflow_jobs.items():
            if self.verbose:
                print(f"Filtering build jobs for repo: {repo}")
            build_jobs[repo] = [self.filter_build_jobs(wf) for wf in wfs]

        os.makedirs('output', exist_ok=True)
        output_path = os.path.join('output', 'build_jobs.json')
        with open(output_path, 'w') as f:
            json.dump(build_jobs, f, indent=4)
        return output_path

    def filter_build_jobs(self, workflow):
        jobs = workflow['jobs']
        build_jobs = []
        for job in jobs:
            if "build" in job['workflow_name'].lower() or "build" in job['name'].lower():
                build_jobs.append(job)
            else:
                for step in job['steps']:
                    if "build" in step['name'].lower():
                        build_jobs.append(job)
                        break
        return {
            'workflow': workflow['workflow'],
            'analysis': workflow['analysis'],
            'jobs': build_jobs
        }

class ExecutionTimePlotter(PipelineStage):
    def __init__(self, verbose=False):
        self.verbose = verbose

    def run(self, input):
        with open(input, 'r') as f:
            build_jobs = json.load(f)

        execution_times = defaultdict(list)

        for repo, wfs in build_jobs.items():
            for wf in wfs:
                for job in wf['jobs']:
                    for step in job['steps']:
                        start_time = isoparse(step['started_at'])
                        end_time = isoparse(step['completed_at'])
                        execution_time = (end_time - start_time).total_seconds()
                        if 'build' in step['name'].lower():
                            execution_times[repo].append(execution_time)

        for repo, times in execution_times.items():
            plt.plot(times, label=repo)
        plt.legend()
        plt.xlabel('Run number')
        plt.ylabel('Execution time (s)')
        plt.title('Execution times of build steps over time')
        plt.savefig('output/execution_times.png')

        return input  # Pass the input through to the next stage

class SuccessRateCalculator(PipelineStage):
    def __init__(self, verbose=False):
        self.verbose = verbose

    def run(self, input):
        with open(input, 'r') as f:
            build_jobs = json.load(f)

        success_rates = {}

        for repo, wfs in build_jobs.items():
            success_count = 0
            total_count = 0
            for wf in wfs:
                for job in wf['jobs']:
                    total_count += 1
                    if job['status'] == 'success':
                        success_count += 1
            success_rates[repo] = success_count / total_count if total_count != 0 else 0

        os.makedirs('output', exist_ok=True)
        output_path = os.path.join('output', 'success_rates.json')
        with open(output_path, 'w') as f:
            json.dump(success_rates, f, indent=4)

        return output_path




def main():
    parser = argparse.ArgumentParser(description='CI Build Performance Analyzer.')
    parser.add_argument('-v', '--verbose', action='store_true',
                        help='increase output verbosity')
    args = parser.parse_args()

    pipeline = [
        RepoParser(),
        WorkflowFilter(),
        WorkflowAnalyser(),
        CIPlotter(),
        JobFetcher(verbose=True),
        BuildJobFilter(verbose=True),
        ExecutionTimePlotter(),
        SuccessRateCalculator()
    ]

    input = 'repos.txt'
    for stage in pipeline:
        if args.verbose:
            print(f"Running {stage.__class__.__name__} stage...")
        input = stage.run(input)
        if args.verbose:
            print(f"Output saved to {input}")


if __name__ == '__main__':
    main()
