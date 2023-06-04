import json
import os
from typing import List, Dict
from analyzers.pipeline.stage import PipelineStage


class RepoMetricsExtractor(PipelineStage):
    def __init__(self, github, args):
        self.github = github
        self.args = args

    def run(self):
        repos = self.read_repos()
        all_repo_details = []

        for repo in repos:
            if self.args.verbose:
                print(f"Extracting metrics for {repo}...")

            repo_details = self.get_repo_details(repo)
            all_repo_details.append({ repo : repo_details})

            # For now, we'll just print them.
            if self.args.verbose:
                print(repo_details)

        # Save all repo details to a JSON file
        output_dir = os.path.join('new_output')
        os.makedirs(output_dir, exist_ok=True)
        with open(os.path.join(output_dir, 'repo_metrics.json'), 'w') as f:
            json.dump(all_repo_details, f, default=str, indent=4)

        if self.args.verbose:
            print(f"Saved repo details to {os.path.join(output_dir, 'repo_metrics.json')}")

    def read_repos(self) -> List[str]:
        with open('../repos.txt', 'r') as f:
            repos = f.read().splitlines()
        return repos

    def get_workflow_details(self, workflow) -> Dict:
        details = {
            'id': workflow.id,
            'name': workflow.name,
            'created_at': workflow.created_at,
            'updated_at': workflow.updated_at,
            'runs_count': workflow.get_runs().totalCount
        }

        return details

    def get_repo_details(self, repo_name: str) -> Dict:
        repo_obj = self.github.get_repo(repo_name)

        workflows = []
        for wf in repo_obj.get_workflows():
            if wf.get_runs().totalCount >= 500:
                workflows.append(self.get_workflow_details(wf))

        workflows = sorted(workflows, key=lambda wf: (
        wf['name'].lower().count('build'), wf['name'].lower().count('test'), wf['name'].lower().count('ci')),
                           reverse=True)
        workflows = workflows[:5] if len(workflows) > 5 else workflows

        details = {
            'workflows': workflows,
            'num_workflows': len(workflows),
            'creation_date': repo_obj.created_at,
            'is_fork': repo_obj.fork,
            'forks': repo_obj.forks_count,
            'language': repo_obj.language,
            'languages': repo_obj.get_languages(),
            'commits': repo_obj.get_commits().totalCount,
            'contributors': repo_obj.get_contributors().totalCount,
            'releases': repo_obj.get_releases().totalCount,
            'size': repo_obj.size
        }

        return details

