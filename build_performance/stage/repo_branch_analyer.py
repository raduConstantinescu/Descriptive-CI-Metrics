from datetime import datetime

import numpy as np

from build_performance.stage.stage import PipelineStage
from build_performance.utils import load_json_data, output_json_data


class RepoBranchesAnalyzer(PipelineStage):
    def __init__(self):
        pass

    def run(self):
        print("RepoBranchesAnalyzer")
        build_performance_data = load_json_data('./output/stats/build_performance_with_main_branch_runs.json')
        data = load_json_data('./output/data.json')

        for repoData in data:
            repositoryName = repoData['repoName']
            for workflow in repoData['workflow']:
                workflowName = workflow['name']
                workflow_performance = build_performance_data[repositoryName][workflowName]
                workflow_performance['branch_performance'] = {}
                for run in reversed(workflow['runs_data']):
                    if run['head_branch'] not in workflow_performance['branch_performance']:
                        workflow_performance['branch_performance'][run['head_branch']] = {
                            'breakage_rate': 0,
                            'mean_resolution_time': 0,
                            'median_resolution_time': 0,
                            'mean_build_resolution': 0,
                            'median_build_resolution': 0,
                            'job_churn': 0,
                            "runs_count" : 0,
                            'runs': []
                        }
                    workflow_performance['branch_performance'][run['head_branch']]['runs'].append({
                        'run_id': run['id'],
                        'run_number': run['run_number'],
                        'conclusion': run['conclusion'],
                        'created_at': datetime.strptime(run['created_at'], '%Y-%m-%dT%H:%M:%S'),
                        'updated_at': datetime.strptime(run['updated_at'], '%Y-%m-%dT%H:%M:%S'),
                        'duration': datetime.strptime(run['updated_at'], '%Y-%m-%dT%H:%M:%S') - datetime.strptime(run['created_at'], '%Y-%m-%dT%H:%M:%S'),
                        'jobs': run['jobs']
                    })

                for branch, branch_performance in workflow_performance['branch_performance'].items():

                    branch_performance['breakage_rate'] = self.calculate_breakage_rate(branch_performance['runs'])
                    branch_performance['mean_resolution_time'], branch_performance['median_resolution_time'] = self.calculate_resolution_time(branch_performance['runs'])
                    branch_performance['mean_build_resolution'], branch_performance['median_build_resolution'] = self.calculate_build_resolution(branch_performance['runs'])
                    branch_performance['job_churn'] = self.calculate_job_churn(branch_performance['runs'])
                    branch_performance['runs_count'] = len(branch_performance['runs'])
                    branch_performance['time_diff'] = self.calculate_first_to_last_run_time(branch_performance['runs'])
                    del branch_performance['runs']

                primary_branch = workflow_performance['metrics']['main_branch']
                primary_branch_breakage_rate = 0
                if primary_branch not in workflow_performance['branch_performance']:
                    print(f"Primary branch {primary_branch} is not in the branch performance list")
                else:
                    primary_branch_breakage_rate = workflow_performance['branch_performance'][primary_branch]['breakage_rate']
                workflow_performance['main_branch_breakage_rate'] = primary_branch_breakage_rate
                workflow_performance['other_branches_breakage_rate_mean'] = 0
                workflow_performance['other_branches_breakage_rate_median'] = 0
                other_branches_count = len(workflow_performance['branch_performance']) - 1
                medians = []
                if other_branches_count > 0:
                    for branch, branch_performance in workflow_performance['branch_performance'].items():
                        if branch != primary_branch:
                            workflow_performance['other_branches_breakage_rate_mean'] += branch_performance['breakage_rate']
                            medians.append(branch_performance['breakage_rate'])
                    workflow_performance['other_branches_breakage_rate_mean'] = workflow_performance['other_branches_breakage_rate_mean'] / other_branches_count
                    workflow_performance['other_branches_breakage_rate_median'] = np.median(medians)
                else:
                    workflow_performance['other_branches_breakage_rate_mean'] = 0

        output_json_data('./output/stats/build_perf_branch.json', build_performance_data)

    def calculate_first_to_last_run_time(self, runs):
        first_run = runs[0]
        last_run = runs[-1]
        time = last_run['updated_at'] - first_run['updated_at']
        return time.total_seconds() // 3600

    def calculate_breakage_rate(self, runs):
        total_runs = len(runs)
        if total_runs > 0:
            failed_runs = 0
            for run in runs:
                if run['conclusion'] == 'failure':
                    failed_runs += 1
            return failed_runs / total_runs
        else:
            return 0

    def calculate_resolution_time(self, runs):
        # keep track of the first failure and find the next success,
        resolution_times = []
        first_failure = None
        for run in runs:
            if run['conclusion'] == 'failure' and first_failure is None:
                first_failure = run
                continue
            if run['conclusion'] == 'success' and first_failure is not None:
                tim_diff_in_minutes = (run['updated_at'] - first_failure['updated_at']).total_seconds() / 60
                resolution_times.append(tim_diff_in_minutes)
                first_failure = None
        if len(resolution_times) > 0:
            return np.mean(resolution_times), np.median(resolution_times)
        else:
            return 0, 0

    def calculate_build_resolution(self, runs):
        # count the number of failing builds between the first failure and the next success
        resolution_times = []
        failed_builds = 0
        first_failure = None
        for run in runs:
            if run['conclusion'] == 'failure' and first_failure is None:
                first_failure = run
                continue
            if run['conclusion'] == 'failure' and first_failure is not None:
                failed_builds += 1
                continue
            if run['conclusion'] == 'success' and first_failure is not None:
                resolution_times.append(failed_builds)
                failed_builds = 0
                first_failure = None
        if len(resolution_times) > 0:
            return np.mean(resolution_times), np.median(resolution_times)
        else:
            return 0, 0


    def calculate_job_churn(self, runs):
        churn = []
        for i in range(len(runs) - 1):
            current_run = runs[i]
            next_run = runs[i + 1]
            current_jobs_shortened = [(job['name'], [(step['name'], step['number']) for step in job['steps']]) for job
                                      in current_run['jobs']]
            next_jobs_shortened = [(job['name'], [(step['name'], step['number']) for step in job['steps']]) for job in
                                   next_run['jobs']]
            added_jobs = [job for job in next_jobs_shortened if job not in current_jobs_shortened]
            removed_jobs = [job for job in current_jobs_shortened if job not in next_jobs_shortened]
            print(f"Added jobs: {added_jobs}")
            print(f"Removed jobs: {removed_jobs}")
            print(f"Added jobs: {len(added_jobs)}")
            print(f"Removed jobs: {len(removed_jobs)}")
            churn.append(len(added_jobs) - len(removed_jobs))
            print(f"Churn: {churn}")

        if churn:  # Check if the churn list is not empty
            print(f"Mean churn: {np.mean(churn)}")
            return np.mean(churn)
        else:  # If the churn list is empty, return 0
            return 0


