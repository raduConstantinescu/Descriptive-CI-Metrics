import os
import json
from github import Github
from github.GithubException import GithubException
from analyzers.stages.stage import PipelineStage

class RepoParser(PipelineStage):
    def __init__(self):
        self.g = Github(os.getenv('GITHUB_ACCESS_TOKEN'))

    def run(self, input):
        with open(os.path.join('../', "repos.txt"), 'r') as f:
            repos = f.read().splitlines()

        results = {}
        failed_repos = []
        for repo in repos:
            try:
                repo_obj = self.g.get_repo(repo)
                workflows = self.get_workflows(repo_obj)
                creation_date = repo_obj.created_at.isoformat()
                results[repo] = {
                    'workflows': workflows,
                    'num_workflows': len(workflows),
                    'creation_date': creation_date,
                    'is_fork': repo_obj.fork,
                    'forks': repo_obj.forks,
                    'language': repo_obj.language,
                    'languages': repo_obj.get_languages(),
                    'commits': repo_obj.get_commits().totalCount,
                    'contributors': repo_obj.get_contributors().totalCount,
                    'releases': repo_obj.get_releases().totalCount,
                    'size': repo_obj.size
                }
            except GithubException as e:
                print(f"Failed to process repository {repo}. Error: {e}")
                failed_repos.append(repo)

        os.makedirs('output', exist_ok=True)
        output_path = os.path.join('output', 'workflows2.json')
        with open(output_path, 'w') as f:
            json.dump(results, f, indent=4)

        # Write failed repos to a separate output file
        failed_repos_path = os.path.join('output', 'failed_repos.txt')
        with open(failed_repos_path, 'w') as f:
            for repo in failed_repos:
                f.write(f"{repo}\n")

        return output_path

    def get_workflows(self, repo):
        workflows = repo.get_workflows()
        result = []
        for wf in workflows:
            result.append({
                'id': wf.id,
                'name': wf.name,
                'created_at': wf.created_at.isoformat(),
                'updated_at': wf.updated_at.isoformat()
            })
        return result

