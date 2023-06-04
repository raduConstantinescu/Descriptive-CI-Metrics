import json

from analyzers.pipeline.stage import PipelineStage


class CIFilter(PipelineStage):
    def __init__(self, args):
        self.verbose = args.verbose

    def run(self):
        print('Cleaning data...')
        data = self._load_data()

        initial_repo_count = len(data)
        cleaned_data = {}
        for repo_name, repo in data.items():
            if len(repo['workflows']) == 0 or repo['num_workflows'] == 0:
                print(f'No workflows for {repo_name}')
                continue
            cleaned_data[repo_name] = repo

        final_repo_count = len(cleaned_data)

        self._save_filtered_data(cleaned_data)

        print(f'Filtered out {initial_repo_count - final_repo_count} repositories without workflows')

    def _load_data(self):
        with open('./new_output/intermediate_results.json') as f:
            data = json.load(f)
        return data

    def _save_filtered_data(self, cleaned_data):
        with open('./new_output/filtered_data.json', 'w') as f:
            json.dump(cleaned_data, f, indent=4)
