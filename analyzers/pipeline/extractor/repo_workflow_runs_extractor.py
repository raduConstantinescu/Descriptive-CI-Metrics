import datetime
import os
import json
import time
from typing import Dict
from github import GithubException
import concurrent.futures

class WorkflowRunExtractor:
    def __init__(self, github, args):
        self.github = github
        self.args = args

    def get_run_details(self, run) -> Dict:
        details = {
            'id': run.id,
            'status': run.status,
            'conclusion': run.conclusion,
            'created_at': run.created_at,
            'updated_at': run.updated_at
        }

        return details

    def get_workflow_runs(self, repo, workflow):
        self.repo = repo  # this line is needed to update self.repo with current repo
        repo_obj = self.github.get_repo(self.repo)
        workflow_id = workflow["id"]
        try:
            workflow_obj = repo_obj.get_workflow(workflow_id)
            if workflow_obj.get_runs().totalCount == 0:
                return
            run_details = []
            max_runs = 600  # change this to the number of runs you want to fetch
            page = 0
            while len(run_details) < max_runs:
                runs = workflow_obj.get_runs().get_page(page)
                if not runs:  # break the loop if no more runs are returned
                    break

                for run in runs:
                    detail = {
                        "id": run.id,
                        "status": run.status,
                        "conclusion": run.conclusion,
                        "created_at": run.created_at,
                        "updated_at": run.updated_at,
                    }
                    run_details.append(detail)

                    if len(run_details) >= max_runs:  # stop adding runs if we've reached the max
                        break

                page += 1  # increment the page number for the next API call

            workflow["runs"] = run_details
        except GithubException as e:
            print(f"Error getting runs for workflow {workflow_id}, error: {str(e)}")

    def update_repo_details(self, repo, repo_details) -> Dict:  # add repo parameter here
        for workflow in repo_details['workflows']:
            self.get_workflow_runs(repo, workflow)  # pass repo parameter here
        return repo_details

    def update_repo_details(self, repo, repo_details) -> Dict:
        with concurrent.futures.ThreadPoolExecutor() as executor:
            # Submit get_workflow_runs tasks for all workflows to the thread pool.
            # Executor.map returns results in the order of the inputs.
            executor.map(lambda workflow: self.get_workflow_runs(repo, workflow),
                         repo_details['workflows'])
        return repo_details

    def run(self):
        # Load repo details from file
        output_dir = os.path.join('new_output')
        with open(os.path.join(output_dir, 'repo_metrics.json'), 'r') as f:
            all_repo_details = json.load(f)

        for repo_details_dict in all_repo_details:
            for repo, details in repo_details_dict.items():
                if details['workflows'] is None or details['num_workflows'] == 0:
                    continue
                updated_details = self.update_repo_details(repo, details)  # pass repo and details here
                repo_details_dict[repo] = updated_details

                if self.args.verbose:
                    print(f"Extracting runs for workflows in {repo}...")
                self.update_repo_details(repo, details)  # pass repo and details here

                rate_limit = self.github.get_rate_limit()
                remaining = rate_limit.core.remaining

                if remaining < 10:
                    reset_timestamp = rate_limit.core.reset
                    reset_time = (reset_timestamp - datetime.datetime.now()).total_seconds()
                    if self.args.verbose:
                        print(f"Rate limit exceeded, sleeping for {reset_time} seconds...")
                    time.sleep(reset_time)

        # Write updated details back to file
        with open(os.path.join(output_dir, 'repo_metrics.json'), 'w') as f:
            json.dump(all_repo_details, f, default=str, indent=4)

        if self.args.verbose:
            print(f"Saved updated repo details to {os.path.join(output_dir, 'repo_metrics.json')}")

