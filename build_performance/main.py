import os
import argparse
import time

from build_performance.stage.repo_generator import RepoGenerator
from utils import load_json_data

from dotenv import load_dotenv
from github import Github


def main():
    parser = argparse.ArgumentParser(description='CI Build Performance Analyzer.')
    parser.add_argument('-v', '--verbose', action='store_true', help='Verbose output.')
    args = parser.parse_args()
    args.verbose = True
    github, config = setup()


    pipeline = [
        RepoGenerator(github, args, config["RepoGenerator"])
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
            print(f"Stage {stage.__class__.__name__} executed in {execution_time} using {used_requests}.")
            print(f"Remaining requests: {end_remaining}")
            print(f"Rate limit resets in {github.get_rate_limit().core.reset}")

    print("Done!")



def setup():
    load_dotenv()
    g = Github(os.getenv('GITHUB_ACCESS_TOKEN'))
    config_data = load_json_data('config.json')
    return g, config_data


if __name__ == '__main__':
    main()