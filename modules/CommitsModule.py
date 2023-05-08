from modules.MiningModule import MiningModule


class CommitsModule(MiningModule):
    def __init__(self, repo):
        self.commits = repo.get_commits()
        self.json = {'commits': {}}

    def mine(self):
        self._extract_commit_count()
        self._extract_commit_messages()

        return self.json

    def _extract_commit_messages(self):
        self.json['commits']['messages'] = [commit.commit.message for commit in self.commits]

    def _extract_commit_count(self):
        self.json['commits']['count'] = self.commits.totalCount
