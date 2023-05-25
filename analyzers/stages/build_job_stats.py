import json
import os
from dateutil.parser import parse

from analyzers.stages.stage import PipelineStage


class BuildStatistics(PipelineStage):
    def __init__(self, verbose=True):
        self.verbose = verbose

    def run(self, input):
        with open(os.path.join('output', 'build_jobs.json'), 'r') as f:
            data = json.load(f)

        build_stats = {}
        for repo_name, repo_data in data.items():
            if self.verbose:
                print(f'Processing repository: {repo_name}')
            for workflow in repo_data['workflows']:
                workflow_name = workflow['name']
                if 'runs' in workflow:
                    for run in workflow['runs']:
                        if 'jobs' in run:
                            for job in run['jobs']:
                                if job['completed_at'] is not None and job['started_at'] is not None:
                                    build_time = parse(job['completed_at']) - parse(job['started_at'])
                                    key = f"{repo_name}_{workflow_name}"
                                    if key not in build_stats:
                                        build_stats[key] = self._initialize_statistics()
                                    build_stats[key]['build_times'].append(build_time.total_seconds())
                                    build_stats[key]['total'] += 1
                                    build_stats[key] = self._update_statistics(job, build_stats[key])
                                else:
                                    continue  # Skip this job as it has incomplete data


        build_stats = self._calculate_aggregate_metrics(build_stats)

        output_file_path = os.path.join('output', 'build_stats.json')
        with open(output_file_path, 'w') as f:
            json.dump(build_stats, f, indent=4)

        return output_file_path

    def _initialize_statistics(self):
        return {
            'build_times': [],
            'successes': 0,
            'total': 0,
            'time_to_recovery': [],
            'last_failure_time': None,
            'failures_since_last_success': 0
        }

    def _update_statistics(self, job, stats):
        if job['conclusion'] == 'success':
            stats['successes'] += 1
            if stats['last_failure_time']:
                recovery_time = parse(job['completed_at']) - stats['last_failure_time']
                stats['time_to_recovery'].append((stats['failures_since_last_success'], recovery_time.total_seconds()))
                stats['last_failure_time'] = None
                stats['failures_since_last_success'] = 0
        else:
            if stats['last_failure_time'] is None:
                stats['last_failure_time'] = parse(job['completed_at'])
            stats['failures_since_last_success'] += 1
        return stats

    def _calculate_aggregate_metrics(self, build_stats):
        for repo_name, stats in build_stats.items():
            stats['average_build_time'] = sum(stats['build_times']) / len(stats['build_times']) if stats['build_times'] else 0
            stats['average_time_to_recovery'] = self._calculate_average_recovery_time(stats)
            stats['success_rate'] = stats['successes'] / stats['total'] * 100 if stats['total'] > 0 else 0
            stats['last_failure_time'] = stats['last_failure_time'].isoformat() if stats['last_failure_time'] else None
            stats['failure_frequency'] = stats['total'] - stats['successes']
            stats['build_flakiness'] = self._calculate_build_flakiness(stats)
            stats['performance_score'] = self._calculate_performance_score(stats)
        return build_stats

    def _calculate_average_recovery_time(self, stats):
        if stats['time_to_recovery']:
            total_recovery_time = sum(time for _, time in stats['time_to_recovery'])
            return total_recovery_time / len(stats['time_to_recovery'])
        else:
            return None

    def _calculate_build_flakiness(self, stats):
        if len(stats['time_to_recovery']) > 0:
            return stats['failure_frequency'] / len(stats['time_to_recovery']) * 100
        else:
            return 0

    def _calculate_performance_score(self, stats):
        if stats['average_time_to_recovery'] is None:
            stats['average_time_to_recovery'] = 0
        if stats['average_build_time'] is None:
            stats['average_build_time'] = 0
        return stats['success_rate'] - 0.5 * stats['average_build_time'] - 0.3 * stats[
            'average_time_to_recovery'] - 0.2 * stats['failure_frequency']


