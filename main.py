"""This is the main (literally) file of the tool. Running this file will mine information."""
import dataclasses
import json
import time
import os
from dotenv import load_dotenv
from github import Github
from modules.mining_module import MiningModule
from modules.commits_module import CommitsModule
from modules.pull_request_module import PullRequestModule


def setup():
    """Sets up external dependencies for the tool. For now, this is just environment loading."""
    load_dotenv()


@dataclasses.dataclass
class RepoInfoExtractor:
    """
    Extracts information from a list of repositories

    Attributes
    ----------
    github : Github
        Github object
    ci_repos : dict
        Dictionary containing information about the repositories
    ci_dir_filter : list
        List of directories to look for CI files in

    Methods
    -------
    extract_info_for_repo(repo_name)
        Extracts information for a given repository
    _extract_yml_files(repo)
        Extracts all the yml files in a repository
    _extract_md_file_content(repo, repo_name)
        Extracts the content of all the md files in a given repository
    """

    def __init__(self, access_token):
        self.github = Github(access_token)
        self.ci_repos = {}
        self.ci_dir_filter = [".circleci", ".github", ".github/workflows"]

    def extract_info_for_repo(self, repo_name):
        """This method extracts information from all modules"""
        repo = self.github.get_repo(repo_name)
        MiningModule.repo = repo

        workflows = repo.get_workflows()
        yml_files = self._extract_yml_files(repo)

        if workflows.totalCount > 0 or yml_files:
            modules = [CommitsModule(), PullRequestModule()]

            self.ci_repos[repo_name] = {
                "repo": repo_name,
                "check_runs": [],
                "md_file_content": []
            }

            for module in modules:
                self.ci_repos[repo_name].update(module.mine())

            self._extract_md_file_content(repo, repo_name)

    def _extract_yml_files(self, repo):
        contents = repo.get_contents("")
        yml_files = []
        while contents:
            file_content = contents.pop(0)
            if file_content.type == "dir" and file_content.name in self.ci_dir_filter:
                contents.extend(repo.get_contents(file_content.path))
            else:
                if file_content.path == ".github/workflows":
                    contents.extend(repo.get_contents(file_content.path))
                if file_content.path.endswith(".yml") or file_content.path.endswith(".yaml"):
                    yml_files.append(file_content)
        return yml_files

    def _extract_md_file_content(self, repo, repo_name):
        contents = repo.get_contents("")
        while contents:
            file_content = contents.pop(0)
            if file_content.type == "dir" and file_content.name in self.ci_dir_filter:
                contents.extend(repo.get_contents(file_content.path))
            else:
                if file_content.path == ".github/workflows":
                    contents.extend(repo.get_contents(file_content.path))
                if file_content.path.endswith(".md"):
                    f_c = self.ci_repos[repo_name]["md_file_content"]
                    f_c.append(file_content.decoded_content.decode("utf-8"))


if __name__ == '__main__':
    setup()
    start = time.time()

    # Read repository names from a file
    with open('repos.txt', encoding="utf-8") as f:
        repos = [line.strip() for line in f.readlines()]

    extractor = RepoInfoExtractor(os.environ.get("GITHUB_ACCESS_TOKEN"))

    for name in repos:
        extractor.extract_info_for_repo(name)

    with open('result.json', 'w', encoding="utf-8") as f:
        json.dump(extractor.ci_repos, f, indent=3)

    end = time.time()

    print("Time taken: ", end - start)
