"""Module for mining workflow information"""
import dataclasses
from enum import Enum
from modules.mining_module import MiningModule
from modules.exception import ModuleParamException


@dataclasses.dataclass
class WorkflowModule(MiningModule):
    """
    This class mines workflow information

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
    # Default behaviour: no params passed: all workflow information extracted.
    def __init__(self, repo, params=None):
        self.workflows = repo.get_workflows()
        self.json = {'workflow_count' : {},
                     'workflows': {}
                     }
        self.params = [c.value for c in WorkflowParams] if params is None else params

    def mine(self):
        """Mines all the data in self.params and returns a dictionary with all the mined data"""
        self._extract_workflow_count()
        for workflow in self.workflows:
            workflow_data = {}
            for param in self.params:
                self._extract_param_info(param=param, workflow=workflow, workflow_data=workflow_data)
            self.json['workflows'][workflow.id] = workflow_data
        return self.json

    # Maps Workflow Param Enum to Param Extractor Function
    def _extract_param_info(self, param, workflow, workflow_data):
        if param in (WorkflowParams.NAME, WorkflowParams.NAME.value):
            self._extract_workflow_name(workflow, workflow_data)
        elif param in (WorkflowParams.ID, WorkflowParams.ID.value):
            self._extract_workflow_id(workflow, workflow_data)
        elif param in (WorkflowParams.CREATED_AT, WorkflowParams.CREATED_AT.value):
            self._extract_workflow_creation_date(workflow, workflow_data)
        elif param in (WorkflowParams.UPDATED_AT, WorkflowParams.UPDATED_AT.value):
            self._extract_workflow_update_date(workflow, workflow_data)
        else:
            raise ModuleParamException("Module does not have param: " + str(param))


    def _extract_workflow_count(self):
        self.json['workflow_count'] = self.workflows.totalCount
    def _extract_workflow_name(self, workflow, workflow_data):
        workflow_data['name'] = workflow.name
    def _extract_workflow_id(self, workflow, workflow_data):
        workflow_data['id'] = workflow.id
    def _extract_workflow_creation_date(self, workflow, workflow_data):
        workflow_data['created_at'] = workflow.created_at.strftime("%Y-%m-%d %H:%M:%S")
    def _extract_workflow_update_date(self, workflow, workflow_data):
        workflow_data['updated_at'] = workflow.updated_at.strftime("%Y-%m-%d %H:%M:%S")


# Parameters of the Workflow
class WorkflowParams(Enum):
    """
    A class that holds enum values for the functions in the WorkflowModule class
    """
    NAME = 'name'
    ID = 'id'
    CREATED_AT = 'created_at'
    UPDATED_AT = 'updated_at'
