import glob
import os

import yaml

from build_performance.stage.stage import PipelineStage
from build_performance.utils import load_json_data, output_json_data

'''
In this class we will see whether the workflows which have quarter data have the fail fast feature enabled or not.
We have their yaml files extracted in output/workflows folder
for each repo, just that we need to change the repo name from /to _ and then we look inside the yaml file at the title
'''


class RepoFailFastExtractor(PipelineStage):
    def __init__(self):
        pass

    def run(self):
        print("RepoFailFastAnalysis")
        build_performance_data = load_json_data('./output/stats/build_performance_with_metrics.json')
        workflows_directory = './output/workflows/'

        included  = 0
        not_included = 0

        true_count = 0
        false_count = 0
        not_found = 0

        for repoName, workflows in build_performance_data.items():
            repositoryName = repoName.replace('/', '_')
            workflow_names = workflows.keys()
            for filename in glob.glob(os.path.join(workflows_directory + repositoryName + '/', '**/*.yml'), recursive=True):
                data = self.parse_yaml(filename)
                if data is not None:
                    if 'name' in data.keys():
                        if data['name'] in workflow_names:
                            has_fail_fast_disabled = self.find_fail_fast(data)
                            jobs_count = self.find_jobs_count(data)
                            if has_fail_fast_disabled:
                                build_performance_data[repoName][data['name']]['fail_fast_disabled'] = True
                            else:
                                build_performance_data[repoName][data['name']]['fail_fast_disabled'] = False
                            build_performance_data[repoName][data['name']]['jobs_count'] = jobs_count
                        else:
                            not_included+=1

        print(f'Included {included} workflows')
        print(f'Not included {not_included} workflows')
        print(f"True count: {true_count}")
        print(f"False count: {false_count}")
        print(f"Not found count: {not_found}")

        output_json_data('./output/stats/build_performance_with_ff.json', build_performance_data)

    def find_jobs_count(self, data):
        if 'jobs' in data:
            return len(data['jobs'])
        else:
            return 0


    def find_fail_fast(self, data):
        if 'jobs' in data:
            for job, job_data in data['jobs'].items():
                if 'strategy' in job_data and 'fail-fast' in job_data['strategy']:
                    if job_data['strategy']['fail-fast'] == False:
                        print(f"Job '{job}' in workflow '{data['name']}' explicitly sets 'fail-fast' to True.")
                        return True
                    else:
                        return False
                else:
                    print(
                        f"Job '{job}' in workflow '{data['name']}' does not explicitly set 'fail-fast'. Default value (True) is used.")
                    return False


    def parse_yaml(self, filename):
        try:
            with open(filename, 'r') as file:
                data = yaml.safe_load(file)
                return data
        except Exception as e:
            print(f'Failed to parse {filename} due to {str(e)}')
            return None



