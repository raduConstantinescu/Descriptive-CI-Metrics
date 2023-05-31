"""Module for mining issue information"""
from enum import Enum

from modules.exception import ModuleParamException
from modules.mining_module import MiningModule


class IssueModule(MiningModule):
    """
    This class mines issue information

    Attributes
    ----------
    issues : PaginatedList[Issue]
        An object where you can extract all kinds of issue information from
    json : dict
        Dictionary containing information about the issues
    params: list
        A list that contains what information you want from the repository in this module

    Methods
    -------
    mine()
        The main entry point to this class. Calling this function will mine all the data in the body
    _extract_param_info(param)
        Calls the right function given a parameter from self.params
    _extract_creation_date()
        Extracts the creation date of the issues
    _extract_close_date()
        Extracts the close date of the issues
    """

    def __init__(self, params=None):
        self.issues = super().repo.get_issues()
        self.json = {'issues': {}}
        self.params = [i.value for i in IssueParams] if params is None else params

    def mine(self):
        for param in self.params:
            if param in (IssueParams.CREATED_AT, IssueParams.CREATED_AT.value):
                self._extract_creation_date()
            elif param in (IssueParams.CLOSED_AT, IssueParams.CLOSED_AT.value):
                self._extract_close_date()
            else:
                raise ModuleParamException("Module does not have param: " + str(param))
        return self.json

    def _extract_creation_date(self):
        self.json['issues']['creation_dates'] = [issue.created_at for issue in self.issues]

    def _extract_close_date(self):
        self.json['issues']['close_dates'] = [issue.closed_at for issue in self.issues]


class IssueParams(Enum):
    """
    A class that holds enum values for the functions in the issue_module class
    """
    CREATED_AT = 'created_at'
    CLOSED_AT = 'closed_at'
