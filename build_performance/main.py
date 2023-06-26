"""
This is the main file for the build performance analysis.
It is used to run the different stages of the analysis pipeline.
The pipeline consists of various steps that can be executed in order.
It contains extraction stages, filtering stages and classification stages.
"""

import os
import argparse
import time

from build_performance.stage.repo_branch_analyer import RepoBranchesAnalyzer
from build_performance.stage.repo_branch_classifier import RepoBranchesClassifier
from build_performance.stage.repo_branches_visualizer import RepoBranchesVisualizer
from build_performance.stage.repo_build_job_extractor import RepoBuildJobExtractor
from build_performance.stage.repo_build_log_extractor import RepoBuildLogExtractor
from build_performance.stage.repo_build_performance_classifier import RepoBuildPerformanceClassifier
from build_performance.stage.repo_cache_extractor import RepoCacheExtractor
from build_performance.stage.repo_day_of_week_analysis import RepoDayOfWeekAnalysis
from build_performance.stage.repo_fail_fast_analysis import RepoFailFastAnalysis
from build_performance.stage.repo_fail_fast_generator import RepoFailFastExtractor
from build_performance.stage.repo_generator import RepoGenerator
from build_performance.stage.repo_main_branch_extractor import RepoMainBranchExtractor
from build_performance.stage.repo_metrics_extractor import RepoMetricsExtractor
from build_performance.stage.repo_project_level_metrics_correlation import RepoProjectLevelMetricsCorrelationAnalysis
from build_performance.stage.repo_project_level_metrics_logistic_regression import \
    RepoProjectLevelMetricsLogisticRegression
from build_performance.stage.repo_runs_analyzer import RepoRunsAnalyzer
from build_performance.stage.repo_runs_classifier import RepoRunsClassifier
from build_performance.stage.repo_skip_usage_analysis import RepoSkipUsageAnalysis
from build_performance.stage.repo_tod_analysis import RepoTODAnalysis
from build_performance.stage.repo_workflow_classifier import RepoWorkflowClassifier
from build_performance.stage.repo_workflow_filter import RepoWorkflowFiltering
# todo: not best practice but works for now
from utils import load_json_data

from dotenv import load_dotenv
from github import Github


def main():
    parser = argparse.ArgumentParser(description='CI Build Performance Analyzer.')
    parser.add_argument('-v', '--verbose', action='store_true', help='Verbose output.')
    parser.add_argument('-d', '--download', action='store_true', help='Download workflow files.')
    parser.add_argument('-a', '--analyze', action='store_true', help='Analyze workflow files.')
    args = parser.parse_args()
    args.verbose = True
    args.download = False
    args.analyze = True
    github, config = setup()


    pipeline = [
        RepoGenerator(github, args, config["RepoGenerator"]),
        RepoWorkflowFiltering(github, args, config["RepoWorkflowFiltering"]),
        RepoMetricsExtractor(github, args, config["RepoMetricsExtractor"]),
        RepoWorkflowClassifier(github, args, config["RepoWorkflowClassifier"]),
        RepoBuildLogExtractor(github, args, config["RepoBuildLogExtractor"]),
        RepoBuildJobExtractor(github, args, config["RepoBuildJobExtractor"]),
        RepoBuildPerformanceClassifier(config["RepoBuildPerformanceClassifier"]),
        RepoTODAnalysis(),
        RepoFailFastExtractor(),
        RepoFailFastAnalysis(),
        RepoCacheExtractor(args),
        RepoMainBranchExtractor(github),
        RepoRunsAnalyzer(),
        RepoRunsClassifier(),
        RepoBranchesAnalyzer(),
        RepoBranchesClassifier(),
        RepoProjectLevelMetricsCorrelationAnalysis(),
        RepoProjectLevelMetricsLogisticRegression(),
        RepoSkipUsageAnalysis(),
        RepoDayOfWeekAnalysis(),
        RepoBranchesVisualizer(),
    ]

    for stage in pipeline:
        print(f"Running {stage.__class__.__name__} stage...")
        start_time = time.time()
        start_remaining = github.get_rate_limit().core.remaining
        stage.run()
        end_time = time.time()
        end_remaining = github.get_rate_limit().core.remaining
        execution_time = end_time - start_time
        used_requests = start_remaining - end_remaining
        if args.verbose:
            print(
                f"Stage {stage.__class__.__name__} executed in {execution_time} seconds using {used_requests} requests.")
            print(f"Remaining requests: {end_remaining}")
            print(f"Rate limit resets at: {github.get_rate_limit().core.reset}")

    print("Done!")


def setup():
    load_dotenv()
    g = Github(os.getenv('GITHUB_ACCESS_TOKEN0'))
    config_data = load_json_data('config.json')
    return g, config_data


if __name__ == '__main__':
    main()