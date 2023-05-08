import json
import time

from github import Github

from modules.CommitsModule import CommitsModule
from modules.PullRequestModule import PullRequestModule


class RepoInfoExtractor:
    """
    Extracts information from a list of repositories

    Attributes
    ----------
    g : Github
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
    _extract_commit_info(repo, repo_name)
        Extracts commit messages for a given repository
    _extract_pull_request_info(repo, repo_name)
        Extracts pull request titles and bodies for a given repository
    _extract_md_file_content(repo, repo_name)
        Extracts the content of all the md files in a given repository
    """

    def __init__(self, access_token):
        self.g = Github(access_token)
        self.ci_repos = {}
        self.ci_dir_filter = [".circleci", ".github", ".github/workflows"]

    def extract_info_for_repo(self, repo_name):
        repo = self.g.get_repo(repo_name)

        workflows = repo.get_workflows()
        yml_files = self._extract_yml_files(repo)

        if workflows.totalCount > 0 or yml_files:
            modules = [CommitsModule(repo), PullRequestModule(repo)]

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
                    self.ci_repos[repo_name]["md_file_content"].append(file_content.decoded_content.decode("utf-8"))


start = time.time()

# Read repository names from a file
with open('repos.txt', encoding="utf-8") as f:
    repos = [line.strip() for line in f.readlines()]

extractor = RepoInfoExtractor("<access_token>")

for repo_name in repos:
    extractor.extract_info_for_repo(repo_name)

with open('result.json', 'w', encoding="utf-8") as f:
    json.dump(extractor.ci_repos, f, indent=3)

end = time.time()

print("Time taken: ", end - start)
