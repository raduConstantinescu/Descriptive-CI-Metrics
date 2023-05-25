"""Module for mining commit information"""
import dataclasses
from enum import Enum

from modules.exception import ModuleParamException
from modules.mining_module import MiningModule
from multiprocessing import Pool
import time


@dataclasses.dataclass
class CommitsModule(MiningModule):
    """
    This class mines commit information

    Parameters
    ----------
    params : list
        List of parameters to mine. Possible values are: 'messages', 'count'

    Attributes
    ----------
    commits : PaginatedList[Commit]
        An object where you can extract all kinds of commit information from
    json : dict
        Dictionary containing information about the commits
    params: list
        A list that contains what information you want from the repository in this module

    Methods
    -------
    mine()
        The main entry point to this class. Calling this function will mine all the data in the body
    _extract_param_info(param)
        Calls the right function given a parameter from self.params
    _extract_commit_messages()
        Extracts all the commit messages from a repository
    _extract_commit_count()
        Extracts the number of commits from a repository
    """

    def __init__(self, params=None):
        self.commits = super().repo.get_commits()
        print(f"Number of commits: {self.commits.totalCount}")
        self.json = {'commits': {}}
        self.params = [c.value for c in CommitParams] if params is None else params

    def mine(self):
        """Mines all the data in self.params and returns a dictionary with all the mined data"""
        start = time.time()
        for param in self.params:
            self._extract_param_info(param)
        end = time.time()
        self.json['commits']['count'] = self.commits.totalCount
        self.json['commits']['time_taken'] = end - start
        return self.json

    def _extract_param_info(self, param):
        if param in (CommitParams.MESSAGES, CommitParams.MESSAGES.value):
            self._extract_commit_messages()
        elif param in (CommitParams.COUNT, CommitParams.COUNT.value):
            self._extract_commit_count()
        else:
            raise ModuleParamException("Module does not have param: " + str(param))

    def _extract_commit_messages(self):
        self.json['commits']['messages'] = [commit.commit.message for commit in self.commits]

    def _extract_commit_count(self):
        self.json['commits']['count'] = self.commits.totalCount


class CommitParams(Enum):
    """
    A class that holds enum values for the functions in the commits_module class
    """
    MESSAGES = 'messages'
    COUNT = 'count'
