import os
import argparse
import time
from github import Github

from analyzers.stages.build_job_filter import BuildJobFilter
from analyzers.stages.build_job_stats_plot import PlotStatistics
from analyzers.stages.build_stats_v2 import BuildStatistics2
from analyzers.stages.job_parser import JobParser
from analyzers.stages.plot_average_build import VisualizeStatistics
from analyzers.stages.plot_builder import PlotBuilder
from analyzers.stages.repo_parser import RepoParser
from analyzers.stages.repo_filter import RepoFilter
from analyzers.stages.workflow_run_parser import WorkflowRunsParser
from analyzers.stages.build_job_stats import BuildStatistics


def main():
    parser = argparse.ArgumentParser(description='CI Build Performance Analyzer.')
    parser.add_argument('-v', '--verbose', action='store_true',
                        help='increase output verbosity')
    args = parser.parse_args()

    # Manually set verbose to True
    args.verbose = True

    g = Github(os.getenv('GITHUB_ACCESS_TOKEN'))

    pipeline = [
        RepoParser(),
        RepoFilter()
        WorkflowRunsParser(True)
        JobParser(),
        BuildJobFilter(True),
        BuildStatistics2(),
        PlotBuilder(),
        PlotStatistics(),
        VisualizeStatistics()
    ]

    input = 'repos.txt'
    for stage in pipeline:
        if args.verbose:
            print(f"Running {stage.__class__.__name__} stage...")
        start_time = time.time()
        start_remaining = g.get_rate_limit().core.remaining
        input = stage.run(input)
        end_time = time.time()
        end_remaining = g.get_rate_limit().core.remaining
        execution_time = end_time - start_time
        used_requests = start_remaining - end_remaining
        if args.verbose:
            print(f"Output saved to {input}")
            print(f"Execution time for {stage.__class__.__name__}: {execution_time} seconds")
            print(f"API requests used for {stage.__class__.__name__}: {used_requests}")
            print(f"API requests remaining: {end_remaining}")


if __name__ == '__main__':
    main()
