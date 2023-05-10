"""Module for mining repository information"""
import dataclasses
from enum import Enum

from modules.exception import ModuleParamException
from modules.mining_module import MiningModule


@dataclasses.dataclass
class RepositoryModule(MiningModule):
    """
    This class mines commit information

    Attributes
    ----------
    json : dict
        Dictionary containing information about the repository

    Methods
    -------
    mine()
        The main entry point to this class. Calling this function will mine all the data in the body
    _extract_param_info(param)
        Calls the right function given a parameter from self.params
    _extract_created_at()
        Extracts the creatation date of a repository
    """

    def __init__(self, params=None):
        self.json = {}
        self.params = [c.value for c in RepositoryParams] if params is None else params

    def mine(self):
        """Mines all the data in self.params and returns a dictionary with all the mined data"""
        for param in self.params:
            self._extract_param_info(param)
        return self.json

    def _extract_param_info(self, param):
        if param in (RepositoryParams.CREATED_AT, RepositoryParams.CREATED_AT.value):
            self._extract_created_at()
        else:
            raise ModuleParamException("Module does not have param: " + str(param))

    def _extract_created_at(self):
        self.json['created_at'] = super().repo.created_at.strftime("%Y-%m-%d %H:%M:%S")


class RepositoryParams(Enum):
    """
    A class that holds enum values for the functions in the repository_module class
    """
    CREATED_AT = 'created_at'
