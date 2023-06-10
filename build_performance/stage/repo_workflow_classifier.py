# The aim of this stage is to rank workflows based on their likelihood of being a build and test workflow.
# Limitation is that commands can be wrapped in scripts or custom build / steps command can be used.

# Starting with 283 repos
# Removed 1213 workflows
# Remaining 68 repos with 106 workflows


import yaml
import glob
import json

from build_performance.stage.scorer import analyze_workflow_scores
from build_performance.stage.stage import PipelineStage
from build_performance.utils import load_json_data, output_json_data
import os


class RepoWorkflowClassifierConfig:
    def __init__(self, config):
        self.input_file = config["input_file"]
        self.workflow_dir = config["workflow_dir"]
        self.output_file = config["output_file"]


class RepoWorkflowClassifier(PipelineStage):
    def __init__(self, github, args, config):
        self.download = args.download
        self.verbose = args.verbose
        self.github = github
        self.config = RepoWorkflowClassifierConfig(config)

    def run(self):
        print("Running RepoWorkflowClassifier")
        data = load_json_data(self.config.input_file)
        if self.download:
            self.download_workflows(data)
        if self.verbose:
            self.show_statistics(data)
        results , results_filtered = self.score_workflows(self.config.workflow_dir)
        self.conclude_repo_data(data, results_filtered)



    def show_statistics(self, data):
        repos_by_language = {}
        for repo in data:
            language = repo["metrics"]["language"]
            if language not in repos_by_language:
                repos_by_language[language] = 0
            repos_by_language[language] += 1
        for language, count in repos_by_language.items():
            print(f"{language}: {count}")

    # lets download starting from a given repo
    def download_workflows(self, data):
        os.makedirs(self.config.workflow_dir, exist_ok=True)

        for repo_info in data:
            repo_name = repo_info["repoName"]
            repo = self.github.get_repo(repo_name)

            # Create a directory for each repository inside workflow_dir


            repo_dir = os.path.join(self.config.workflow_dir, repo_name.replace('/', '_'))
            # if the directory already exists skip to next repository
            if os.path.exists(repo_dir):
                continue
            os.makedirs(repo_dir, exist_ok=True)

            # Assuming workflow files are in .github/workflows/ directory
            try:
                contents = repo.get_contents(".github/workflows")
                for content_file in contents:
                    if content_file.path.endswith('.yaml') or content_file.path.endswith('.yml'):
                        print(f"Downloading from repo {repo_name} workflow {content_file.name}...")

                        # Get the content of the file
                        content = content_file.decoded_content.decode()

                        # Write the content to a local file
                        with open(os.path.join(repo_dir, content_file.name), 'w') as f:
                            f.write(content)

            except Exception as e:
                print(f"Error occurred when trying to download workflows from {repo_name}: {str(e)}")

        print("Workflows downloaded.")

    def score_workflows(self, workflow_dir):
        return analyze_workflow_scores(workflow_dir)

    def conclude_repo_data(self, data, workflows):
        print(f"Starting with {len(data)} repos")
        count = 0
        repos_to_remove = []

        for repo in data:
            repo_name = repo["repoName"]
            repo_name_to_file_name = repo_name.replace('/', '_')
            if repo_name_to_file_name in workflows:
                workflows_in_repo = []
                for workflow_of_data in repo['workflow'][:]:
                    workflow_score = next((item for item in workflows[repo_name_to_file_name] if
                                           item["workflow_name"] == workflow_of_data["name"]), None)
                    if workflow_score is None:
                        count += 1
                        print(f"Removing {workflow_of_data} from {repo_name}")
                        repo['workflow'].remove(workflow_of_data)
                    else:
                        workflows_in_repo.append((workflow_of_data, workflow_score['score']))
                # Only keep up to 4 workflows with highest scores
                workflows_in_repo.sort(key=lambda x: x[1], reverse=True)
                repo['workflow'] = [item[0] for item in workflows_in_repo[:4]]
                if len(repo['workflow']) == 0:
                    repos_to_remove.append(repo)
            else:
                repos_to_remove.append(repo)



        for repo in repos_to_remove:
            data.remove(repo)
            count += len(repo['workflow'])

        remaining_workflows = 0
        for repo in data:
            remaining_workflows += len(repo['workflow'])

        print(f"Removed {count} workflows")
        print(f"Remaining {len(data)} repos with {remaining_workflows} workflows")
        output_json_data(self.config.output_file, data)



















