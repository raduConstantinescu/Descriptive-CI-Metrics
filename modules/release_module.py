"""Module for mining release information"""
from enum import Enum

from modules.exception import ModuleParamException
from modules.mining_module import MiningModule


class ReleaseModule(MiningModule):
    """
    This class mines release information

    Attributes
    ----------
    releases : PaginatedList[GitRelease]
        An object where you can extract all kinds of release information from
    json : dict
        Dictionary containing information about the releases
    params: list
        A list that contains what information you want from the repository in this module

    Methods
    -------
    mine()
        The main entry point to this class. Calling this function will mine all the data in the body
    _extract_param_info(param)
        Calls the right function given a parameter from self.params
    _extract_release_date()
        Extracts the publishing date of all releases
    """

    def __init__(self, params=None):
        self.releases = super().repo.get_releases()
        self.json = {'releases': {}}
        self.params = [r.value for r in ReleaseParams] if params is None else params

    def mine(self):
        for param in self.params:
            if param in (ReleaseParams.DATE, ReleaseParams.DATE.value):
                self._extract_release_date()
            else:
                raise ModuleParamException("Module does not have param: " + str(param))
        return self.json

    def _extract_release_date(self):
        self.json['releases']['dates'] = [release.published_at for release in self.releases]


class ReleaseParams(Enum):
    """
    A class that holds enum values for the functions in the release_module class
    """
    DATE = 'date'
