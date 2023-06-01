import argparse
import json
import os
import time

from dotenv import load_dotenv
from github import Github

from analyzers.pipeline.job_extractor import JobExtractor
from analyzers.pipeline.repo_generator import RepoGenerator, RepoGeneratorConfig
from analyzers.pipeline.repo_metrics_extractor import RepoMetricsExtractor
from analyzers.pipeline.repo_workflow_runs_extractor import WorkflowRunExtractor


def main():
    parser = argparse.ArgumentParser(description='CI Build Performance Analyzer.')
    parser.add_argument('-v', '--verbose', action='store_true', help='increase output verbosity')
    parser.add_argument('-s', '--stats', action='store_true', help='print stats about the pipeline stage')
    parser.add_argument('-stage', '--stage', type=int, help='run a specific stage in the pipeline')
    parser.add_argument('-start', '--start', type=int, help='start from a specific repo')
    args = parser.parse_args()

    g, config_data = setup()
    pipeline = [
        RepoGenerator(g, args, RepoGeneratorConfig(config_data["RepoGenerator"])),
        RepoMetricsExtractor(g, args),
        WorkflowRunExtractor(g, args),
        JobExtractor(g, args)
    ]

    if args.stage:
        pipeline = [pipeline[args.stage]]

    for stage in pipeline:
        if args.verbose:
            print(f"Running {stage.__class__.__name__} stage...")
        start_time = time.time()
        start_remaining = g.get_rate_limit().core.remaining
        stage.run()
        end_time = time.time()
        end_remaining = g.get_rate_limit().core.remaining
        execution_time = end_time - start_time
        used_requests = start_remaining - end_remaining
        if args.verbose:
            print(f"Output saved to {input}")
            print(f"Execution time for {stage.__class__.__name__}: {execution_time} seconds")
            print(f"API requests used for {stage.__class__.__name__}: {used_requests}")
            print(f"API requests remaining: {end_remaining}")

    print("Done!")

def setup():
    load_dotenv()
    g = Github(os.getenv('GITHUB_ACCESS_TOKEN'))
    with open('config.json') as f:
        config_data = json.load(f)
    return g, config_data


if __name__ == '__main__':
    main()
