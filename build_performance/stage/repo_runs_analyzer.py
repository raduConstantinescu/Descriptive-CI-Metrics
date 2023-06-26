from build_performance.stage.stage import PipelineStage
from build_performance.utils import load_json_data, output_json_data


class RepoRunsAnalyzer(PipelineStage):
    def __init__(self):
        pass

    def run(self):
        print("RepoRunsAnalyzer")
        build_performance_data = load_json_data('./output/stats/build_performance_with_main_branch.json')
        data = load_json_data('./output/data.json')

        for repoData in data:
            repositoryName = repoData['repoName']
            for workflow in repoData['workflow']:
                workflowName = workflow['name']
                workflow_performance = build_performance_data[repositoryName][workflowName]
                workflow_performance['main_branch_runs'] = 0
                workflow_performance['other_branch_runs'] = 0
                workflow_performance['main_branch_percentage'] = 0
                workflow_performance['run_performance'] = {}

                workflow_performance.pop('run_conclusions', None)
                workflow_performance.pop('run_durations', None)

                for run in workflow['runs_data']:
                    if run['run_attempt'] not in workflow_performance['run_performance']:
                        workflow_performance['run_performance'][run['run_attempt']] = {
                            'breakage_rate' : 0,
                            'conclusions' : [],
                        }
                        workflow_performance['run_performance'][run['run_attempt']]['conclusions'].append(run['conclusion'])
                    else:
                        workflow_performance['run_performance'][run['run_attempt']]['conclusions'].append(run['conclusion'])
                    if run['head_branch'] == workflow_performance['metrics']['main_branch']:
                        workflow_performance['main_branch_runs'] += 1
                    else:
                        workflow_performance['other_branch_runs'] += 1
                # here we calculate the breakage rate for each run attempt
                for run_attempt, run_data in workflow_performance['run_performance'].items():
                    total_runs = len(run_data['conclusions'])
                    if total_runs > 0:
                        run_data['breakage_rate'] = run_data['conclusions'].count('failure') / total_runs
                    else:
                        run_data['breakage_rate'] = 0
                    del run_data['conclusions']
                # here we calculate the percentage of runs that come from the main branch
                total_runs = workflow_performance['main_branch_runs'] + workflow_performance['other_branch_runs']
                if total_runs > 0:
                    workflow_performance['main_branch_percentage'] = workflow_performance['main_branch_runs'] / total_runs
                else:
                    workflow_performance['main_branch_percentage'] = 0

        output_json_data('./output/stats/build_performance_with_main_branch_runs.json', build_performance_data)
