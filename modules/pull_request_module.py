"""Module for mining pull request information"""
import dataclasses
from modules.mining_module import MiningModule


@dataclasses.dataclass
class PullRequestModule(MiningModule):
    """
    This class mines commit information

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
    _extract_pull_request_titles()
        Extracts all pull request titles from a repository
    _extract_commit_count()
        Extracts all pull request bodies from a repository
    """

    def __init__(self):
        self.pulls = super().repo.get_pulls(state='all')
        self.json = {'pull_requests': {}}

    def mine(self):
        """Mines all the data in the body and returns a dictionary with all the mined data"""
        self._extract_pull_request_titles()
        self._extract_pull_request_bodies()

        return self.json

    def _extract_pull_request_titles(self):
        self.json['pull_requests']['titles'] = [pull.title for pull in self.pulls]

    def _extract_pull_request_bodies(self):
        self.json['pull_requests']['bodies'] = [pull.body for pull in self.pulls]
