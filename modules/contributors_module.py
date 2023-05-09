"""Module for mining contributor information"""
from enum import Enum

from modules.exception import ModuleParamException
from modules.mining_module import MiningModule


class ContributorsModule(MiningModule):
    """
    This class can be used to extract information about the contributors for a repository,
    including the number of users that have contributed to the repository and the total
    number of contributions per user.

     Attributes
    ----------
    repo: Repository
        The repository object to be analyzed.
    params: dict
        A list of parameters specifying the type of information to extract.

    Methods
    -------
    mine(): Extracts the specified information from the repository object and returns
            a JSON object containing the results.
    _extract_param_info(param):
        Calls the right function given a parameter from self.params
    _extract_contributors_count():
        Extracts the total number of contributors to the repository.
    _extract_contributions_per_contributor():
        Extracts the total number of contributions per contributor to the repository.
    """
    def __init__(self, repo, params):
        self.contributors = repo.get_contributors()
        self.json = {'contributors': {}}
        self.params = params

    def mine(self):
        for param in self.params:
            self._extract_param_info(param=param)
        return self.json

    def _extract_param_info(self, param):
        if param == ContributorsParams.COUNT:
            self._extract_contributors_count()
        elif param == ContributorsParams.CONTRIBUTION_COUNT:
            self._extract_contributions_per_contributor()
        else:
            raise ModuleParamException("Module does not have param: " + str(param))

    def _extract_contributors_count(self):
        self.json['contributors']['count'] = self.contributors.totalCount

    def _extract_contributions_per_contributor(self):
        self.json['contributors']['contributions_per_contributor'] = \
            [(contributor.login, contributor.contributions) for contributor in self.contributors]


class ContributorsParams(Enum):
    """
    A class that holds enum values for the functions in the contributors class
    """
    COUNT = 'count'
    CONTRIBUTION_COUNT = 'contributions_per_contributor'
