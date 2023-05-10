"""Module for mining workflow information"""
import dataclasses
from enum import Enum
from modules.mining_module import MiningModule
from modules.exception import ModuleParamException


@dataclasses.dataclass
class WorkflowModule(MiningModule):
    """
    This class mines commit information

    Attributes
    ----------
    workflows : PaginatedList[Workflow]
        An object where you can extract all kinds of workflow information from
    json : dict
        Dictionary containing information about the workflows
    params: list
        A list that contains what information you want from the repository in this module.

    Methods
    -------
    mine()
        The main entry point to this class. Calling this function will mine all the data in
        self.params.
    _extract_workflow_count()
        Extracts the number of workflows from a repository
    _extract_workflow_name()
        Extracts the workflow names from a repository
    _self._extract_workflow_id()
        Extracts the workflows ids.
    self._extract_workflow_creation_date()
        Extracts workflow creation date.
    self._extract_workflow_update_date()
        Extracts workflow update date.
    """

    # Params, represent the information you want extracted from the Workflow Module.
    def __init__(self, repo, params=None):
        self.workflows = repo.get_workflows()
        self.json = {'workflows': {}}
        self.params = [c.value for c in WorkflowParams] if params is None else params

    def mine(self):
        """Mines all the data in self.params and returns a dictionary with all the mined data"""
        for param in self.params:
            self._extract_param_info(param=param)
        return self.json

    # Maps Workflow Param Enum to Param Extractor Function
    def _extract_param_info(self, param):
        if param in (WorkflowParams.COUNT, WorkflowParams.COUNT.value):
            self._extract_workflow_count()
        elif param in (WorkflowParams.NAME, WorkflowParams.NAME.value):
            self._extract_workflow_name()
        elif param in (WorkflowParams.ID, WorkflowParams.ID.value):
            self._extract_workflow_id()
        elif param in (WorkflowParams.CREATED_AT, WorkflowParams.CREATED_AT.value):
            self._extract_workflow_creation_date()
        elif param in (WorkflowParams.UPDATED_AT, WorkflowParams.UPDATED_AT.value):
            self._extract_workflow_update_date()
        else:
            raise ModuleParamException("Module does not have param: " + str(param))

    def _extract_workflow_count(self):
        self.json['workflows']['count'] = self.workflows.totalCount
    def _extract_workflow_name(self):
        self.json['workflows']['name'] = [workflow.name for workflow in self.workflows]
    def _extract_workflow_id(self):
        self.json['workflows']['id'] = [workflow.id for workflow in self.workflows]
    # Example of possible date retrieved: "2021-03-03 20:24:01"
    def _extract_workflow_creation_date(self):
        self.json['workflows']['created_at'] = [workflow.created_at.strftime("%Y-%m-%d %H:%M:%S") for workflow in self.workflows]
    def _extract_workflow_update_date(self):
        self.json['workflows']['updated_at'] = [workflow.updated_at.strftime("%Y-%m-%d %H:%M:%S") for workflow in self.workflows]


# Parameters of the Workflow
class WorkflowParams(Enum):
    """
    A class that holds enum values for the functions in the WorkflowModule class
    """
    COUNT = 'count'
    NAME = 'name'
    ID = 'id'
    CREATED_AT = 'created_at'
    UPDATED_AT = 'updated_at'
