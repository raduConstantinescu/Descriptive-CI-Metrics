import time

import github
from github import Github
from dotenv import load_dotenv
import matplotlib.pyplot as plt
import os
import json
import re
import argparse

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
