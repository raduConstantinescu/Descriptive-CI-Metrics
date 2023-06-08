from analyzers.pipeline.stage import PipelineStage
from ... import utils
import os


class WorkflowDownloaderConfig():
    def __init__(self, config):
        self.input_file = config["input_file"]
        self.output_dir = config["output_dir"]


class WorkflowDownloader(PipelineStage):
    def __init__(self, args, config, github):
        self.args = args
        self.config = config
        self.github = github

    def run(self):
        data = utils.load_data(self.config.input_file)

        # Create output_dir if not exists
        os.makedirs(self.config.output_dir, exist_ok=True)

        # keys here are all repo names
        for repo_name, repo in data.items():
            repo = self.github.get_repo(repo_name)

            # Create a directory for each repository inside output_dir
            repo_dir = os.path.join(self.config.output_dir, repo_name.replace('/', '_'))
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

