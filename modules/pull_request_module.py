"""Module for mining pull request information"""
import dataclasses
from enum import Enum

from modules.exception import ModuleParamException
from modules.mining_module import MiningModule


@dataclasses.dataclass
class PullRequestModule(MiningModule):
    """
    This class mines pull request information from a repository

    Parameters
    ----------
    params : list
        List of parameters to mine. Possible values are: 'titles', 'bodies'

    Attributes
    ----------
    pulls : PaginatedList[PullRequest]
        An object where you can extract all kinds of pull request information from
    json : dict
        Dictionary containing information about the pull requests

    Methods
    -------
    mine()
        The main entry point to this class. Calling this function will mine all the data in the body
    _extract_param_info(param)
        Calls the right function given a parameter from self.params
    _extract_pull_request_titles()
        Extracts the titles of the pull requests from a repository
    _extract_pull_request_bodies()
        Extracts the bodies of the pull requests from a repository
    """

    def __init__(self, params=None):
        self.pulls = super().repo.get_pulls(state='all')
        self.json = {'pull_requests': {}}
        self.params = [c.value for c in PullRequestParams] if params is None else params

    def mine(self):
        """Mines all the data in self.params and returns a dictionary with all the mined data"""
        for param in self.params:
            self._extract_param_info(param)
        return self.json

    def _extract_param_info(self, param):
        if param in (PullRequestParams.TITLES, PullRequestParams.TITLES.value):
            self._extract_pull_request_titles()
        elif param in (PullRequestParams.BODIES, PullRequestParams.BODIES.value):
            self._extract_pull_request_bodies()
        elif param in (PullRequestParams.COUNT_CLOSED, PullRequestParams.COUNT_CLOSED.value):
            self._extract_count_merged_pull_requests()
        else:
            raise ModuleParamException("Module does not have param: " + str(param))

    def _extract_pull_request_titles(self):
        self.json['pull_requests']['titles'] = [pull.title for pull in self.pulls]

    def _extract_pull_request_bodies(self):
        self.json['pull_requests']['bodies'] = [pull.body for pull in self.pulls]

    def _extract_count_merged_pull_requests(self):
        self.json['pull_requests']['count_closed'] = sum(1 for pull in self.pulls if pull.closed_at is not None)


class PullRequestParams(Enum):
    """
    A class that holds enum values for the functions in the commits_module class
    """
    TITLES = 'titles'
    BODIES = 'bodies'
    COUNT_CLOSED = 'count_closed'
