import statistics
from datetime import datetime

from analyzers.pipeline.stage import PipelineStage
from ...utils import load_data, output_data

class CIAnalyzerConfig:
    def __init__(self, config):
        self.input_file = config["input_file"]
        self.output_file = config["output_file"]
        self.stats_file = config["stats_file"]

class CIAnalyzer(PipelineStage):
    def __init__(self, args, config: CIAnalyzerConfig):
        self.verbose = args.verbose
        self.config = config

    def run(self):
        data = load_data(self.config.input_file)
        ci_data = self.analyze_data(data)
        output_data(self.config.output_file, ci_data)
        self.output_stats(ci_data)

    def analyze_data(self, data):
        ci_data = {}

        # Iterate over each repository
        for repo_name, repo in data.items():
            # Iterate over each workflow
            for workflow in repo['workflows']:
                total_time = 0
                conclusions = {}
                workflow_runs = []

                # Iterate over each run
                for run in workflow['runs']:
                    # Calculate total execution time

                    created_at = datetime.strptime(run['created_at'], '%Y-%m-%d %H:%M:%S')
                    updated_at = datetime.strptime(run['updated_at'], '%Y-%m-%d %H:%M:%S')
                    execution_time = (updated_at - created_at).total_seconds()
                    total_time += execution_time

                    # Count conclusion types
                    if run['conclusion'] in conclusions:
                        conclusions[run['conclusion']] += 1
                    else:
                        conclusions[run['conclusion']] = 1

                    # Append workflow run data to the list
                    workflow_runs.append({
                        'created_at': run['created_at'],
                        'execution_time': execution_time,
                        'conclusion': run['conclusion']
                    })

                median_time = statistics.median([run['execution_time'] for run in workflow_runs])
                average_time = total_time / len(workflow['runs']) if workflow['runs'] else 0

                # Calculate success rate for successful conclusions
                success_rate = conclusions.get('success', 0) / sum(conclusions.values()) if conclusions else 0

                # Construct the key as "reponame-workflowname-id"
                key = f"{repo_name}-{workflow['name']}-{workflow['id']}"

                breakages_rate = conclusions.get('failure', 0) / sum(conclusions.values()) if conclusions else 0
                # things might be 0/0, so we need to check for that
                breakages_rate_only_success = 0
                if conclusions.get('failure', 0) + conclusions.get('success', 0) > 0:
                    breakages_rate_only_success = conclusions.get('failure', 0) / (conclusions.get('failure', 0) + conclusions.get('success', 0))
                ci_data[key] = {
                    'median_execution_time' : median_time,
                    'average_execution_time': average_time,
                    'success_rate': success_rate,
                    'breakages_rate': breakages_rate,
                    'breakages_rate_only_success': breakages_rate_only_success,
                    'conclusions': conclusions,
                    'workflow_runs': workflow_runs
                }

        return ci_data

    def output_stats(self, ci_data):
        success_rates = []
        exec_times = []
        breakages_rates = []
        for key, value in ci_data.items():
            success_rates.append(value['success_rate'])
            exec_times.append(value['average_execution_time'])
            breakages_rates.append(value['breakages_rate'])

        overall_stats = {
            'median_breakages_rate': statistics.median(breakages_rates),
            'average_success_rate': sum(success_rates) / len(success_rates),
            'median_success_rate': statistics.median(success_rates),
            'average_execution_time': sum(exec_times) / len(exec_times),
            'median_execution_time': statistics.median(exec_times)
        }

        output_data(self.config.stats_file, overall_stats)