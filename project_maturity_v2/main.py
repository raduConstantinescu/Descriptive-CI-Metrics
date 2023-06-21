import os

from dotenv import load_dotenv
from github import Github

from project_maturity_v2.extractors.pull_requests_extractor import PullRequestsExtractor


def setup():
    """Sets up external dependencies for the tool. For now, this is just environment loading."""
    load_dotenv()


def main(github):
    # RepositoryExtractor(github, 1000).extract()
    # MetricsExtractor(github).extract()
    # RepoFileAnalyzer(github).count_files()
    # RepositoryFilter().filter()
    PullRequestsExtractor(github).extract()

if __name__ == "__main__":
    setup()
    g = Github(os.environ.get("GITHUB_ACCESS_TOKEN2"))
    main(g)