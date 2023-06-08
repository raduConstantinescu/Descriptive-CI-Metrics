import os

from dotenv import load_dotenv
from github import Github

from repository_extractor import RepositoryExtractor


def setup():
    """Sets up external dependencies for the tool. For now, this is just environment loading."""
    load_dotenv()


def main(github):
    repositories = RepositoryExtractor(github, 5000).extract()

if __name__ == "__main__":
    setup()
    g = Github(os.environ.get("GITHUB_ACCESS_TOKEN"))
    main(g)