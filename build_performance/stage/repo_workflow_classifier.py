# The aim of this stage is to rank workflows based on their likelihood of being a build and test workflow.
# Limitation is that commands can be wrapped in scripts or custom build / steps command can be used.
import yaml
import glob
import json

from build_performance.stage.stage import PipelineStage
from build_performance.utils import load_json_data
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
        self.score_workflows()
        print("Scoring statistics:")
        for score_type, count in self.scores.items():
            print(f"{score_type}: {count}")

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

    def score_workflows(self):
        # Mapping from workflow names to scores
        name_scores = {"node js ci": 5, "java ci": 5}  # Add other names with scores here

        # Mapping from job names to scores
        job_scores = {"build": 15}  # Add other job names with scores here

        # Mapping from step names to scores
        step_scores = {"Build with Gradle": 15, "Build with Maven": 15}  # Add other steps names with scores here

        # Mapping from run commands to scores
        run_scores = {}

        # Integrate the given keywords into run_scores
        build_keywords = {
            "JavaScript": ["npm install", "npm ci", "npm build", "npm test", "npm run",
                           "yarn install", "yarn build", "yarn test", "yarn run"],
            "TypeScript": ["tsc", "ts-node", "npm install", "npm ci", "npm build",
                           "npm test", "npm run", "yarn install", "yarn build",
                           "yarn test", "yarn run"],
            "Java": ["mvn install", "mvn clean install", "mvn test",
                     "mvn clean test", "mvn package", "mvn clean package",
                     "mvn compile", "gradle build", "gradle test", "gradle install",
                     "gradle clean", "gradle check", "ant compile", "ant test",
                     "ant build", "ant install"]
        }
        for score, commands in zip([50, 100, 200], build_keywords.values()):
            for command in commands:
                run_scores[command] = score

        scores = {}

        # Walk the directory containing all the workflows
        for filename in glob.glob(os.path.join(self.config.workflow_dir, '**/*.yml'), recursive=True):
            with open(filename, 'r') as file:
                try:
                    # Parse the workflow YAML
                    workflow = yaml.safe_load(file)
                except yaml.YAMLError as e:
                    print(f"Could not parse {filename}: {e}")
                    continue

                # Initialize score for this workflow
                score = 0

                # Score name
                name = workflow.get('name', '')
                score += name_scores.get(name.lower(), 0)

                # Score jobs
                for job in workflow.get('jobs', {}).values():
                    # Score job name
                    job_name = job.get('name', '')
                    score += job_scores.get(job_name.lower(), 0)

                    # Score steps
                    for step in job.get('steps', []):
                        # Score step name
                        step_name = step.get('name', '')
                        score += step_scores.get(step_name.lower(), 0)

                        # Score run command
                        run_command = step.get('run', '')
                        if isinstance(run_command, str):
                            for command, command_score in run_scores.items():
                                if command in run_command.lower():
                                    score += command_score

                # Add the score to the scores dictionary
                repo_name = filename.split(os.sep)[-2].replace('_', '/')
                workflow_name = filename.split(os.sep)[-1]
                if repo_name not in scores:
                    scores[repo_name] = {}
                scores[repo_name][workflow_name] = score

        # Save scores to JSON
        with open(self.config.output_file, 'w') as f:
            json.dump(scores, f, indent=4)

        # Save scores
        self.scores = scores















