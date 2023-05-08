from enum import Enum
from modules.MiningModule import MiningModule

class WorkflowParams(Enum):
    COUNT = 'count'
    NAME = 'name'
class WorkflowModule(MiningModule):
    def __init__(self, repo, params):
        self.workflows = repo.get_workflows()
        self.json = {'workflows': {}}
        self.params = params

    def mine(self):
        map(self.params, self._extract_param_info())
        return self.json

    def _extract_param_info(self, param):
        match param:
            case WorkflowParams.COUNT:
                self._extract_workflow_count()
            case WorkflowParams.NAME:
                self._extract_workflow_name()
            case _:
                return "Invalid param for Workflow Module"

    def _extract_workflow_count(self):
        self.json['workflows']['count'] = self.workflows.totalCount

    def _extract_workflow_name(self):
        self.json['workflows']['name'] = [workflow.name for workflow in self.workflows]
