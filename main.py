"""This is the main (literally) file of the tool. Running this file will mine information."""
import dataclasses
import json
import os
import time
import threading
import queue
import sys

from dotenv import load_dotenv
from github import Github

from github.GithubException import RateLimitExceededException
from modules.commits_module import CommitsModule
from modules.mining_module import MiningModule
from modules.pull_request_module import PullRequestModule


def add_input(input_queue):
    while True:
        input_queue.put(sys.stdin.read(1))


def setup():
    """Sets up external dependencies for the tool. For now, this is just environment loading."""
    load_dotenv()
    # Start a thread to read stdin so that we can exit gracefully
    input_queue = queue.Queue()
    input_thread = threading.Thread(target=add_input, args=(input_queue,))
    input_thread.daemon = True
    input_thread.start()
    return input_queue


def write_to_file(extractor, filename, keep_existing_data=False):
    if keep_existing_data:
        already_extracted = []
        if os.path.exists(filename):
            with open(output_file, 'r', encoding="utf-8") as f:
                already_extracted = json.load(f)

        for repo in already_extracted:
            extractor.ci_repos[repo] = already_extracted[repo]

    with open(output_file, 'w', encoding="utf-8") as f:
        json.dump(extractor.ci_repos, f, indent=3, default=str)


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

    def __init__(self, access_token, include_non_ci=False, verbose=False):
        self.github = Github(access_token)
        self.ci_repos = {}
        self.ci_dir_filter = [".circleci", ".github", ".github/workflows"]
        self.include_non_ci = include_non_ci
        self.counter = 0
        self.verbose = verbose

        if self.verbose:
            print("Extractor initialized. Requests remaining: ", self.github.get_rate_limit().core.remaining)

    def _mine_repo(self, ci, repo_name):
        modules = [CommitsModule(), PullRequestModule(['titles'])]

        self.ci_repos[repo_name] = {
            "repo": repo_name,
            "ci": ci
        }

        for module in modules:
            self.ci_repos[repo_name].update(module.mine())

    def extract_info_for_repo(self, repo_name):
        """This method extracts information from all modules"""
        self._check_rate_limit()

        self.counter += 1
        ci = False

        repo = self.github.get_repo(repo_name)
        MiningModule.repo = repo

        if self.verbose:
            print(f"Extracting info for {repo_name} (repo number {self.counter})")
            if self.counter % 10 == 0:
                print(f"Requests remaining: {self.github.get_rate_limit().core.remaining}")

        workflows = repo.get_workflows()
        yml_files = self._extract_yml_files(repo)

        if workflows.totalCount > 0 or yml_files:
            ci = True

        if ci or self.include_non_ci:
            try:
                self._mine_repo(ci, repo_name)
            except RateLimitExceededException:
                if self.verbose:
                    print("Rate limit exceeded")
                self._check_rate_limit()
                self._mine_repo(ci, repo_name)

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

    def _check_rate_limit(self):
        requests_remaining = self.github.get_rate_limit().core.remaining
        # threshold of 100 requests remaining before we sleep
        if requests_remaining < 100:
            rt = self.github.get_rate_limit()
            # reset timestamp timezone does not match current timezone
            # so we calculate the difference modulo 3600 to get the seconds until the next hour reset
            sleep_for = 3600 - (abs(rt.core.reset.timestamp() - time.time()) % 3600)
            # 2 minutes buffer
            sleep_for += 120

            print("Sleeping for: ", sleep_for / 60)
            time.sleep(sleep_for)


if __name__ == '__main__':
    input_queue = setup()
    start = time.time()
    output_file = "testing.json"

    # Read repository names from a file
    with open('repos.txt', encoding="utf-8") as f:
        repos = [line.strip() for line in f.readlines()]

    extractor = RepoInfoExtractor(os.environ.get("GITHUB_ACCESS_TOKEN"), include_non_ci=True, verbose=True)

    for name in repos:
        # User can press q to stop the extraction and save the current state
        if not input_queue.empty() and input_queue.get() == 'q':
            break
        try:
            extractor.extract_info_for_repo(name)
        # pylint: disable=broad-except
        except Exception as e:
            print(f"Error for {name}: {e}")
            continue
    
    write_to_file(extractor, output_file, keep_existing_data=True)

    end = time.time()

    print("Time taken: ", end - start)
