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
        Extract the number of contributions for the top 50% contributors to the repository,
         who also have more than 10 commits.
    """
    def __init__(self, params, top_percentage_of_contributors=0.5):
        self.repo = super().repo
        self.contributors = self.repo.get_contributors()
        self.json = {'contributors': {}}
        self.params = params
        self.top_percentage_of_contributors = top_percentage_of_contributors

    def mine(self):
        for param in self.params:
            self._extract_param_info(param=param)
        return self.json

    def _extract_param_info(self, param):
        if param in (ContributorsParams.COUNT, ContributorsParams.COUNT.value):
            self._extract_contributors_count()
        elif param in (ContributorsParams.CONTRIBUTION_COUNT,
                       ContributorsParams.CONTRIBUTION_COUNT.value):
            self._extract_contributions_per_contributor()
        else:
            raise ModuleParamException("Module does not have param: " + str(param))

    def _extract_contributors_count(self):
        self.json['contributors']['count'] = self.contributors.totalCount


    def _extract_contributions_per_contributor(self):
        sorted_contributors = sorted(self.contributors, key=lambda x: x.contributions, reverse=True)
        top_percentage = int(len(sorted_contributors) * self.top_percentage_of_contributors)
        filtered_contributors = [(contributor.login, contributor.contributions)
                                 for contributor in sorted_contributors[:top_percentage]]

        self.json['contributors']['contributions_per_contributor'] = filtered_contributors


class ContributorsParams(Enum):
    """
    A class that holds enum values for the functions in the contributors class
    """
    COUNT = 'count'
    CONTRIBUTION_COUNT = 'contributions_per_contributor'
