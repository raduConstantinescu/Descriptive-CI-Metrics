from build_performance.stage.stage import PipelineStage
from build_performance.utils import load_json_data
import pandas as pd


class RepoBranchesVisualizer(PipelineStage):
    def __init__(self):
        pass

    def run(self):

        data = load_json_data('./output/stats/quadrant_branches_processed3.json')

        # Flatten the dictionary and create a DataFrame
        data_list = []
        for quadrant, branches in data.items():
            for branch_type, metrics in branches.items():
                row = {'quadrant': quadrant, 'branch_type': branch_type}
                row.update(metrics)
                data_list.append(row)

        df = pd.DataFrame(data_list)

        # Select the required columns
        df_selected = df[['quadrant', 'branch_type', 'mean_breakage_rates', 'median_resolution_times', 'mean_build_resolutions', 'mean_job_churns', 'mean_runs_counts']]

        latex_table = df_selected.to_latex(index=False, float_format="%.2f")

        print(latex_table)