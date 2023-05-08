from enum import Enum
from modules.MiningModule import MiningModule
from modules.Exception import ModuleParamException
class WorkflowModule(MiningModule):
    # Params, represent the information you want extracted from the Workflow Module.
    def __init__(self, repo, params):
        self.workflows = repo.get_workflows()
        self.json = {'workflows': {}}
        self.params = params

    def mine(self):
        for param in self.params:
            self._extract_param_info(param = param)
        return self.json

    # Maps Workflow Param Enum to Param Extractor Function
    def _extract_param_info(self, param):
        if param == WorkflowParams.COUNT:
            self._extract_workflow_count()
        elif param == WorkflowParams.NAME:
            self._extract_workflow_name()
        else:
            raise ModuleParamException("Module does not have param: " + str(param))

    def _extract_workflow_count(self):
        self.json['workflows']['count'] = self.workflows.totalCount

    def _extract_workflow_name(self):
        self.json['workflows']['name'] = [workflow.name for workflow in self.workflows]

# Parameters of the Workflow
# TODO: Extend with Rest necessary information.
class WorkflowParams(Enum):
    COUNT = 'count'
    NAME = 'name'