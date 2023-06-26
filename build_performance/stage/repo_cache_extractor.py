import glob
import os
import pandas as pd

from build_performance.stage.stage import PipelineStage
from build_performance.utils import load_json_data, parse_yaml, output_json_data


class RepoCacheExtractor(PipelineStage):
    def __init__(self, args):
        self.args = args
        pass

    def run(self):
        print("RepoCacheExtractor")
        workflows_directory = './output/workflows/'
        if not self.args.analyze:
            build_performance_data = load_json_data('./output/stats/build_performance_with_ff.json')
            for repoName, workflows in build_performance_data.items():
                repositoryName = repoName.replace('/', '_')
                workflow_names = workflows.keys()
                for filename in glob.glob(os.path.join(workflows_directory + repositoryName + '/', '**/*.yml'), recursive=True):
                    data = parse_yaml(filename)
                    if data is not None:
                        if 'name' in data.keys():
                            if data['name'] in workflow_names:
                                has_cache = self.find_cache(data)
                                if has_cache:
                                    build_performance_data[repoName][data['name']]['cache'] = True
                                else:
                                    build_performance_data[repoName][data['name']]['cache'] = False
                            else:
                                print(f"{data['name']} not found in {repoName}")
            output_json_data('./output/stats/build_performance_with_cache.json', build_performance_data)
        else:
            build_performance_data = load_json_data('./output/stats/build_performance_with_cache.json')
            # todo analyze the data
            quadrant_workflows_by_caching = {}
            for repoName, workflows in build_performance_data.items():
                for workflowName, workflowData in workflows.items():
                    quadrant = workflowData['quadrant']
                    if quadrant not in quadrant_workflows_by_caching:
                        quadrant_workflows_by_caching[quadrant] = {
                            'cache' : 0,
                            'no_cache' : 0,
                        }

                    cache = workflowData['cache']
                    if cache is True:
                        quadrant_workflows_by_caching[quadrant]['cache'] += 1
                    else:
                        quadrant_workflows_by_caching[quadrant]['no_cache'] += 1

            print(quadrant_workflows_by_caching)
            df = self.create_table(quadrant_workflows_by_caching)
            print(df.to_latex(index=False))

    def create_table(self, data):
        table_data = []

        for quadrant, quadrant_data in data.items():
            cache = quadrant_data['cache']
            no_cache = quadrant_data['no_cache']
            total = cache + no_cache
            cache_percentage = (cache / total) * 100 if total != 0 else 0
            no_cache_percentage = (no_cache / total) * 100 if total != 0 else 0
            table_data.append([quadrant, no_cache_percentage])

        df = pd.DataFrame(table_data,
                          columns=['Quadrant', 'No Cache %'])

        df['No Cache %'] = df['No Cache %'].map("{:.2f}%".format)

        return df

    def find_cache(self, data):
        if 'jobs' in data:
            for job, job_data in data['jobs'].items():
                if 'steps' in job_data:
                    for step in job_data['steps']:
                        if 'uses' in step:
                            if 'cache' in step['uses'] or 'setup' in step['uses']:
                                return True
        return False