from build_performance.stage.stage import PipelineStage
from build_performance.utils import load_json_data
import pandas as pd

class RepoFailFastAnalysis(PipelineStage):
    def __init__(self):
        pass

    def run(self):
        print("RepoFailFastAnalysis")
        build_performance_data = load_json_data('./output/stats/build_performance_with_ff.json')
        quadrant_workflows_by_fail_fast = {}

        for repoName, workflows in build_performance_data.items():
            for workflowName, workflowData in workflows.items():
                quadrant = workflowData['quadrant']
                if quadrant not in quadrant_workflows_by_fail_fast:
                    quadrant_workflows_by_fail_fast[quadrant] = {
                        'enabled' : 0,
                        'disabled' : 0,
                    }

                fail_fast = workflowData['fail_fast_disabled']
                if fail_fast is True:
                    quadrant_workflows_by_fail_fast[quadrant]['disabled'] += 1
                else:
                    quadrant_workflows_by_fail_fast[quadrant]['enabled'] += 1

        print(quadrant_workflows_by_fail_fast)
        df = self.create_table(quadrant_workflows_by_fail_fast)
        print(df.to_latex(index=False))

    def create_table(self, data):
        table_data = []

        for quadrant, quadrant_data in data.items():
            enabled = quadrant_data['enabled']
            disabled = quadrant_data['disabled']
            total = enabled + disabled
            enabled_percentage = (enabled / total) * 100 if total != 0 else 0
            disabled_percentage = (disabled / total) * 100 if total != 0 else 0
            table_data.append([quadrant, enabled, disabled, enabled_percentage, disabled_percentage])

        df = pd.DataFrame(table_data,
                          columns=['Quadrant', 'Fail Fast Enabled', 'Fail Fast Disabled', 'Enabled %', 'Disabled %'])

        df['Enabled %'] = df['Enabled %'].map("{:.2f}%".format)
        df['Disabled %'] = df['Disabled %'].map("{:.2f}%".format)

        return df

