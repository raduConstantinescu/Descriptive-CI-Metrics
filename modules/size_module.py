"""Module for mining size information"""
from enum import Enum

from modules.commits_module import CommitsModule, CommitParams
from modules.contributors_module import ContributorsModule, ContributorsParams
from modules.exception import ModuleParamException
from modules.mining_module import MiningModule


class SizeModule(MiningModule):
    """
    Module for mining size information

    Attributes:
        repo: Repository
            The repository object for which size information is to be extracted.
        params: dict
            A list of parameters to extract. Valid options are:
            REPO_SIZE, COUNT_FILES, COUNT_DIRECTORIES, COUNT_BRANCHES,
             COUNT_COMMITS, COUNT_CONTRIBUTORS.

    Methods:
        mine():
            Extracts information based on the list of parameters and returns a JSON object.
        _extract_param_info(param):
            Extracts the specified parameter's information from the repository and adds it
            to the JSON object.
        _extract_repo_size():
            Extracts the size of the repository.
        _extract_number_of_files():
            Extracts the count of files in the repository.
        _extract_number_of_directories():
            Extracts the count of directories in the repository, including nested directories.
        _count_dirs(directory):
            Recursive function to count the number of directories in the repository.
        _extract_number_of_branches():
            Extracts the count of branches in the repository.
        _extract_commit_count():
            Extracts the count of commits in the repository.
        _extract_contributors_count():
            Extracts the count of contributors in the repository.
    """
    def __init__(self, params):
        self.repo = super().repo
        self.repo_contents = self.repo.get_contents("")
        self.json = {'size': {}}
        self.params = params

    def mine(self):
        for param in self.params:
            self._extract_param_info(param=param)
        return self.json

    def _extract_param_info(self, param):
        if param in (SizeParams.REPO_SIZE, SizeParams.REPO_SIZE.value):
            self._extract_repo_size()
        elif param in (SizeParams.COUNT_FILES, SizeParams.COUNT_FILES.value):
            self._extract_number_of_files()
        elif param in (SizeParams.COUNT_DIRECTORIES, SizeParams.COUNT_DIRECTORIES.value):
            self._extract_number_of_directories()
        elif param in (SizeParams.COUNT_BRANCHES, SizeParams.COUNT_BRANCHES.value):
            self._extract_number_of_branches()
        elif param in (SizeParams.COUNT_COMMITS, SizeParams.COUNT_COMMITS.value):
            self._extract_commit_count()
        elif param in (SizeParams.COUNT_CONTRIBUTORS, SizeParams.COUNT_CONTRIBUTORS.value):
            self._extract_contributors_count()
        else:
            raise ModuleParamException("Module does not have param: " + str(param))

    def _extract_repo_size(self):
        size = self.repo.size
        self.json['size']['repos_size'] = size

    def _extract_number_of_files(self):
        file_count = len(self.repo_contents)
        self.json['size']['file_count'] = file_count

    def _extract_number_of_directories(self):
        directories_count = self._count_dirs(self.repo_contents)
        self.json['size']['directories_count'] = directories_count

    def _count_dirs(self, directory):
        num_dirs = 0
        for item in directory:
            if item.type == "dir":
                num_dirs += 1
                num_dirs += self._count_dirs((self.repo.get_contents(item.path)))
        return num_dirs

    def _extract_number_of_branches(self):
        branch_count = self.repo.get_branches().totalCount
        self.json['size']['branch_count'] = branch_count

    def _extract_commit_count(self):
        commit_module = CommitsModule([CommitParams.COUNT])
        commit_count = commit_module.mine()
        key = next(iter(commit_count))
        value = commit_count[key]
        self.json['size']["commits_count"] = value['count']

    def _extract_contributors_count(self):
        contributors_module = ContributorsModule([ContributorsParams.COUNT])
        contributors_count = contributors_module.mine()
        key = next(iter(contributors_count))
        value = contributors_count[key]
        self.json['size']["contributors_count"] = value['count']


class SizeParams(Enum):
    """
    A class that holds enum values for the functions in the size class
    """
    REPO_SIZE = 'repo_size'
    COUNT_FILES = 'count_files'
    COUNT_DIRECTORIES = 'count_directories'
    COUNT_BRANCHES = 'count_branches'
    COUNT_COMMITS = 'count_commits'
    COUNT_CONTRIBUTORS = 'count_contributors'
