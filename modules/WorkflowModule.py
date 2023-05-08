from modules.MiningModule import MiningModule


class WorkflowModule(MiningModule):
    def __init__(self, repo):
        self.workflows = repo.get_workflows()
        self.json = {'workflows': {}}

    def mine(self):
        self._extract_workflow_count()
        self._extract_workflow_name()
        return self.json

    def _extract_workflow_count(self):
        self.json['workflows']['count'] = self.workflows.totalCount

    def _extract_workflow_name(self):
        self.json['workflows']['name'] = [workflow.name for workflow in self.workflows]
