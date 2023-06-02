import argparse
import json
import os

from dotenv import load_dotenv
from github import Github

from extractor.Generator import Generator
from utils import log_info

def main():
    g, config_data = setup()
    parser = argparse.ArgumentParser(description='Repository generator')
    parser.add_argument('-v', '--verbose', action='store_true', help='increase output verbosity')
    args = parser.parse_args()
    args.verbose = True

    Generator(args, g, config_data).run()


def setup():
    load_dotenv()
    g = Github(os.getenv('GITHUB_ACCESS_TOKEN'))
    with open('config.json') as f:
        config_data = json.load(f)
    return g, config_data

if __name__ == '__main__':
    main()