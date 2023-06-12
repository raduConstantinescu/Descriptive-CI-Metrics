import os
import argparse
import time

# todo: not best practice but works for now
from build_performance.stage import *
from build_performance.stage.repo_build_job_extractor import RepoBuildJobExtractor
from build_performance.stage.repo_build_log_extractor import RepoBuildLogExtractor
from build_performance.stage.repo_build_performance_classifier import RepoBuildPerformanceClassifier
from build_performance.stage.repo_generator import RepoGenerator
from build_performance.stage.repo_metrics_extractor import RepoMetricsExtractor
from build_performance.stage.repo_workflow_classifier import RepoWorkflowClassifier
from build_performance.stage.repo_workflow_filter import RepoWorkflowFiltering
from utils import load_json_data

from dotenv import load_dotenv
from github import Github


def main():
    parser = argparse.ArgumentParser(description='CI Build Performance Analyzer.')
    parser.add_argument('-v', '--verbose', action='store_true', help='Verbose output.')
    parser.add_argument('-d', '--download', action='store_true', help='Download workflow files.')
    args = parser.parse_args()
    args.verbose = True
    args.download = False
    github, config = setup()


    pipeline = [
        # RepoGenerator(github, args, config["RepoGenerator"]),
        # RepoWorkflowFiltering(github, args, config["RepoWorkflowFiltering"]),
        # RepoMetricsExtractor(github, args, config["RepoMetricsExtractor"]),
        # RepoWorkflowClassifier(github, args, config["RepoWorkflowClassifier"]),
        # RepoBuildLogExtractor(github, args, config["RepoBuildLogExtractor"]),
        # RepoBuildJobExtractor(github, args, config["RepoBuildJobExtractor"]),
        RepoBuildPerformanceClassifier(args, config["RepoBuildPerformanceClassifier"]),
    ]

    for stage in pipeline:
        if args.verbose:
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
    g = Github(os.getenv('GITHUB_ACCESS_TOKEN3'))
    config_data = load_json_data('config.json')
    return g, config_data


if __name__ == '__main__':
    main()