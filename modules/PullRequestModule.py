from modules.MiningModule import MiningModule


class PullRequestModule(MiningModule):
    def __init__(self, repo):
        self.pulls = repo.get_pulls(state='all')
        self.json = {'pull_requests': {}}

    def mine(self):
        self._extract_pull_request_titles()
        self._extract_pull_request_bodies()

        return self.json

    def _extract_pull_request_titles(self):
        self.json['pull_requests']['titles'] = [pull.title for pull in self.pulls]

    def _extract_pull_request_bodies(self):
        self.json['pull_requests']['bodies'] = [pull.body for pull in self.pulls]
