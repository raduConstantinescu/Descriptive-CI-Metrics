from enum import Enum

from modules.Exception import ModuleParamException
from modules.MiningModule import MiningModule


# This module can be used to extract information about the contributors for a repository
# Currently it supports extracting information about:
#     - the number of users that have contributed to a repository
#     - the total number of contributions per user
class ContributorsModule(MiningModule):
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
        self.json['contributors']['contributions_per_contributor'] = [(contributor.login, contributor.contributions) for
                                                                      contributor in self.contributors]


class ContributorsParams(Enum):
    COUNT = 'count'
    CONTRIBUTION_COUNT = 'contributions_per_contributor'
