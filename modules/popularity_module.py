from enum import Enum

from modules.Exception import ModuleParamException
from modules.MiningModule import MiningModule

# This module helps extract data that is believed to indicate information about a project's popularity, namely:
#     - number of stars
#     - number of watchers
#     - number of forks
# This can be extended with other information retrieval methods if considered appropriate for describing a project's
# popularity.
class PopularityModule(MiningModule):
    def __init__(self, repo, params):
        self.repo = repo
        self.json = {'popularity': {}}
        self.params = params

    def mine(self):
        for param in self.params:
            self._extract_param_info(param=param)
        return self.json

    def _extract_param_info(self, param):
        if param == PopularityParams.STAR_COUNT:
            self._extract_star_count()
        elif param == PopularityParams.WATCHERS_COUNT:
            self._extract_watchers_count()
        elif param == PopularityParams.FORKS_COUNT:
            self._extract_forks_count()
        else:
            raise ModuleParamException("Module does not have param: " + str(param))

    def _extract_star_count(self):
        self.json['popularity']['star_count'] = self.repo.get_stargazers().totalCount

    def _extract_watchers_count(self):
        self.json['popularity']['watchers_count'] = self.repo.get_subscribers().totalCount

    def _extract_forks_count(self):
        self.json['popularity']['forks_count'] = self.repo.forks_count


class PopularityParams(Enum):
    STAR_COUNT = 'stars_count'
    WATCHERS_COUNT = 'watchers_count'
    FORKS_COUNT = 'forks_count'
