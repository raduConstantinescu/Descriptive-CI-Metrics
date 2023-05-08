"""Module for mining commit information"""
import dataclasses
from modules.mining_module import MiningModule


@dataclasses.dataclass
class CommitsModule(MiningModule):
    """
    This class mines commit information

    Attributes
    ----------
    commits : PaginatedList[Commit]
        An object where you can extract all kinds of commit information from
    json : dict
        Dictionary containing information about the commits

    Methods
    -------
    mine()
        The main entry point to this class. Calling this function will mine all the data in the body
    _extract_commit_messages()
        Extracts all the commit messages from a repository
    _extract_commit_count()
        Extracts the number of commits from a repository
    """

    def __init__(self):
        self.commits = super().repo.get_commits()
        self.json = {'commits': {}}

    def mine(self):
        """Mines all the data in the body and returns a dictionary with all the mined data"""
        self._extract_commit_count()
        self._extract_commit_messages()

        return self.json

    def _extract_commit_messages(self):
        self.json['commits']['messages'] = [commit.commit.message for commit in self.commits]

    def _extract_commit_count(self):
        self.json['commits']['count'] = self.commits.totalCount
