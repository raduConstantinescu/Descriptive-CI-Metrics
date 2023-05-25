import json
import os
from dateutil.parser import parse

from analyzers.stages.stage import PipelineStage


class BuildStatistics2(PipelineStage):
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
                                    build_stats[key]['number_of_builds'] += 1
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
            'number_of_builds': 0,
            'successes': 0,
            'time_to_recovery': [],
            'last_failure_time': None,
            'failures_since_last_success': 0
        }

    def _update_statistics(self, job, stats):
        if job['conclusion'] == 'success':
            stats['successes'] += 1
            if stats['last_failure_time']:
                recovery_time = parse(job['completed_at']) - parse(stats['last_failure_time'])
                stats['time_to_recovery'].append((stats['failures_since_last_success'], recovery_time.total_seconds()))
                stats['last_failure_time'] = None
                stats['failures_since_last_success'] = 0
        else:
            if stats['last_failure_time'] is None:
                stats['last_failure_time'] = parse(job['completed_at']).isoformat()
            stats['failures_since_last_success'] += 1
        return stats

    def _calculate_aggregate_metrics(self, build_stats):
        for repo_name, stats in build_stats.items():
            stats['average_build_time'] = sum(stats['build_times']) / len(stats['build_times']) if stats[
                'build_times'] else 0
            stats['success_rate'] = stats['successes'] / stats['number_of_builds'] * 100 if stats[
                                                                                                'number_of_builds'] > 0 else 0
            stats['time_to_first_pass'] = [recovery_time for _, recovery_time in stats['time_to_recovery']]
            stats['builds_to_pass'] = [builds for builds, _ in stats['time_to_recovery']]
            stats['performance_score'] = self._calculate_performance_score(stats)

        # Normalize performance score in a second pass
        scores = [repo_stats['performance_score'] for repo_stats in build_stats.values()]
        min_score = min(scores)
        max_score = max(scores)

        for repo_name, stats in build_stats.items():
            stats['performance_score'] = (stats['performance_score'] - min_score) / (
                        max_score - min_score) if max_score != min_score else 0

        return build_stats

    def _calculate_performance_score(self, stats):
        return stats['success_rate'] - 0.5 * stats['average_build_time']
