"""Module for mining popularity information"""
from enum import Enum

from modules.exception import ModuleParamException
from modules.mining_module import MiningModule


class PopularityModule(MiningModule):
    """
    This module extracts data that is believed to indicate information about a project's popularity:
    - number of stars
    - number of watchers
    - number of forks
    This can be extended with other information retrieval methods if
     considered appropriate for describing a project's popularity.

    Attributes:
        repo: Repository
            The repository object for which popularity information is to be extracted.
        params: dict
            A list of parameters to extract. Valid options are:
            STAR_COUNT, WATCHERS_COUNT, FORKS_COUNT.

    Methods:
        mine():
            Extracts information based on the list of parameters and returns a JSON object.
        _extract_param_info(param):
            Extracts the specified parameter's information from the repository
            and adds it to the JSON object.
        _extract_star_count():
            Extracts the number of stars for the repository.
        _extract_watchers_count():
            Extracts the number of watchers for the repository.
        _extract_forks_count():
            Extracts the number of forks for the repository.
    """
    def __init__(self, params=None):
        self.repo = super().repo
        self.json = {'popularity': {}}
        self.params = [p.value for p in PopularityParams] if params is None else params

    def mine(self):
        for param in self.params:
            self._extract_param_info(param=param)
        return self.json

    def _extract_param_info(self, param):
        if param in (PopularityParams.STAR_COUNT, PopularityParams.STAR_COUNT.value):
            self._extract_star_count()
        elif param in (PopularityParams.WATCHERS_COUNT,PopularityParams.WATCHERS_COUNT.value):
            self._extract_watchers_count()
        elif param in (PopularityParams.FORKS_COUNT, PopularityParams.FORKS_COUNT.value):
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
    """
    A class that holds enum values for the functions in the popularity class
    """
    STAR_COUNT = 'stars_count'
    WATCHERS_COUNT = 'watchers_count'
    FORKS_COUNT = 'forks_count'
