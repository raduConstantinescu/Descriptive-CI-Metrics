import yaml
import os
import json
from analyzers.pipeline.stage import PipelineStage

class WorkflowScoreConfig:
    def __init__(self, config):
        self.input_file = config["input_file"]
        self.workflow_dir = config["workflow_dir"]
        self.output_file = config["output_file"]

class WorkflowScore(PipelineStage):
    def __init__(self, args, config):
        self.args = args
        self.config = config

    def run(self):
        # Define the common keywords
        keywords = {
            'default': ['build', 'test', 'ci', 'compile', 'install'],
            'python': ['pip', 'pytest', 'flask', 'django'],
            'java': ['maven', 'gradle', 'spring', 'junit'],
            'javascript': ['npm', 'node', 'mocha', 'jasmine'],
            'typescript': ['npm', 'node', 'mocha', 'jasmine', 'tsc'],
        }

        # Load the languages data
        with open(self.config.input_file) as file:
            languages_data = json.load(file)

        # Create the results dictionary
        results = {}

        # Iterate over the directories in workflow_dir
        for repo_name in os.listdir(self.config.workflow_dir):
            repo_dir = os.path.join(self.config.workflow_dir, repo_name)

            # Skip files and non-directories
            if not os.path.isdir(repo_dir):
                continue

            # Get the language for this repo
            language = languages_data.get(repo_name, {}).get('language', 'default')

            # Initialize the dictionary for this repo
            results[repo_name] = {}

            # Iterate over the files in the repo directory
            for workflow_file in os.listdir(repo_dir):
                # Skip directories and non-YAML files
                if not os.path.isfile(os.path.join(repo_dir, workflow_file)) or not workflow_file.endswith('.yml'):
                    continue

                # Load the YAML file
                with open(os.path.join(repo_dir, workflow_file)) as file:
                    workflow = yaml.safe_load(file)

                # Start the score
                score = 0

                # Check the name of the workflow
                for keyword in keywords[language]:
                    if keyword in workflow.get('name', '').lower():
                        score += 1

                # Check the jobs of the workflow
                for job in workflow.get('jobs', {}).values():
                    # Check for the presence of a strategy matrix
                    if 'strategy' in job and 'matrix' in job['strategy']:
                        score += 5

                    for step in job.get('steps', []):
                        for keyword in keywords[language]:
                            if keyword in step.get('name', '').lower():
                                score += 1
                            if keyword in str(step.get('run', '')).lower():
                                score += 1

                # Store the score for this workflow
                results[repo_name][workflow_file] = score

        # Writing the results to the output file
        with open(self.config.output_file, 'w') as output_file:
            json.dump(results, output_file, indent=4)
