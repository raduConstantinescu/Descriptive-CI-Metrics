from build_performance.stage.stage import PipelineStage
from build_performance.utils import load_json_data, output_json_data
import numpy as np

class RepoSkipUsageAnalysis(PipelineStage):
    def __init__(self):
        pass

    def run(self):
        data = load_json_data('./output/stats/build_performance_with_main_branch.json')

        workflows_by_skip_usage = {}

        for repoName, repoData in data.items():
            for workflowName, workflowData in repoData.items():
                quadrant = workflowData['quadrant']
                if quadrant not in workflows_by_skip_usage:
                    workflows_by_skip_usage[quadrant] = {
                        'skip_usage' : 0,
                        'total' : 0,
                        'skip_usage_percentage' : 0,
                    }
                if 'skipped' in workflowData['conclusion_set']:
                    workflows_by_skip_usage[quadrant]['skip_usage'] += 1
                workflows_by_skip_usage[quadrant]['total'] += 1

        for quadrant, quadrantData in workflows_by_skip_usage.items():
            quadrantData['skip_usage_percentage'] = np.round(quadrantData['skip_usage'] / quadrantData['total'] * 100, 2)

        print(workflows_by_skip_usage)

        output_json_data('./output/stats/build_performance_with_main_branch_skip_usage.json', workflows_by_skip_usage)







