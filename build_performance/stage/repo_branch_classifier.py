import numpy as np
import pandas as pd
from matplotlib import pyplot as plt

from build_performance.stage.stage import PipelineStage
from build_performance.utils import load_json_data, output_json_data

'''
We will classify again workflows based on which quadrant they belong to
we will look in each quadrant, for a workflow what is the the branch performance of the workflow,
we will group all 'main_branches' and the others and we calculate for the others the average
'''

class RepoBranchesClassifier(PipelineStage):
    def __init__(self):
        pass

    def run(self):
        data = load_json_data('./output/stats/build_perf_branch.json')

        quadrant_workflows_by_branch_perf = {}
        for repoName, repoData in data.items():
            for workflowName, workflowData in repoData.items():
                main_branch = workflowData['metrics']['main_branch']
                quadrant = workflowData['quadrant']
                if quadrant not in quadrant_workflows_by_branch_perf:
                    quadrant_workflows_by_branch_perf[quadrant] = {}
                if 'main_branch' not in quadrant_workflows_by_branch_perf[quadrant]:
                    quadrant_workflows_by_branch_perf[quadrant]['main_branch'] = {
                        'breakage_rates': [],
                        "mean_resolution_times": [],
                        "median_resolution_times": [],
                        "mean_build_resolutions": [],
                        "median_build_resolutions": [],
                        "job_churns": [],
                        "runs_counts": []
                    }
                if 'other_branches' not in quadrant_workflows_by_branch_perf[quadrant]:
                    quadrant_workflows_by_branch_perf[quadrant]['other_branches'] = {
                        'breakage_rates': [],
                        "mean_resolution_times": [],
                        "median_resolution_times": [],
                        "mean_build_resolutions": [],
                        "median_build_resolutions": [],
                        "job_churns": [],
                        "runs_counts": [],
                    }
                # iterate over branches in branch_performance
                for branch, branchData in workflowData['branch_performance'].items():
                    if branch == main_branch:
                        # append the data
                        quadrant_workflows_by_branch_perf[quadrant]['main_branch']['breakage_rates'].append(branchData['breakage_rate'])
                        quadrant_workflows_by_branch_perf[quadrant]['main_branch']['mean_resolution_times'].append(branchData['mean_resolution_time'])
                        quadrant_workflows_by_branch_perf[quadrant]['main_branch']['median_resolution_times'].append(branchData['median_resolution_time'])
                        quadrant_workflows_by_branch_perf[quadrant]['main_branch']['mean_build_resolutions'].append(branchData['mean_build_resolution'])
                        quadrant_workflows_by_branch_perf[quadrant]['main_branch']['median_build_resolutions'].append(branchData['median_build_resolution'])
                        quadrant_workflows_by_branch_perf[quadrant]['main_branch']['job_churns'].append(branchData['job_churn'])
                        quadrant_workflows_by_branch_perf[quadrant]['main_branch']['runs_counts'].append(branchData['runs_count'])
                    else:
                        # append the data
                        quadrant_workflows_by_branch_perf[quadrant]['other_branches']['breakage_rates'].append(branchData['breakage_rate'])
                        quadrant_workflows_by_branch_perf[quadrant]['other_branches']['mean_resolution_times'].append(branchData['mean_resolution_time'])
                        quadrant_workflows_by_branch_perf[quadrant]['other_branches']['median_resolution_times'].append(branchData['median_resolution_time'])
                        quadrant_workflows_by_branch_perf[quadrant]['other_branches']['mean_build_resolutions'].append(branchData['mean_build_resolution'])
                        quadrant_workflows_by_branch_perf[quadrant]['other_branches']['median_build_resolutions'].append(branchData['median_build_resolution'])
                        quadrant_workflows_by_branch_perf[quadrant]['other_branches']['job_churns'].append(branchData['job_churn'])
                        quadrant_workflows_by_branch_perf[quadrant]['other_branches']['runs_counts'].append(branchData['runs_count'])

        quadrant_workflows_number_of_other_branhces = {}

        for repoName, repoData in data.items():
            for workflowName, workflowData in repoData.items():
                quadrant = workflowData['quadrant']
                if quadrant not in quadrant_workflows_number_of_other_branhces:
                    quadrant_workflows_number_of_other_branhces[quadrant] = []

                quadrant_workflows_number_of_other_branhces[quadrant].append(len(workflowData['branch_performance'].keys()))

        for quadrant, quadrantData in quadrant_workflows_number_of_other_branhces.items():
            # round to 2 decimals
            mean = np.round(np.mean(quadrantData), 2)
            median = np.round(np.median(quadrantData), 2)
            quadrant_workflows_number_of_other_branhces[quadrant] = {
                'mean': mean,
                'median': median
            }

        print(quadrant_workflows_number_of_other_branhces)



        output_json_data('./output/stats/quadrant_branches.json', quadrant_workflows_by_branch_perf)

        filtered_data = self.filter_outliers(quadrant_workflows_by_branch_perf, 'runs_counts', 70)


        processed_data = self.process_data(filtered_data)
        pd = self.make_dataframe(processed_data)

        latex_output = pd.to_latex(index=False,
                                   caption="Summary of branch metrics by quadrant",
                                   label="tab:summary",
                                   float_format="{:0.2f}".format,
                                   longtable=True)


        latex_output = latex_output.replace("\\toprule", "\\topline")
        latex_output = latex_output.replace("\\midrule", "\\midline")
        latex_output = latex_output.replace("\\bottomrule", "\\bottomline")

        print(latex_output)

    def filter_outliers(self, data, metric_key, percentile):
        sizes_before = []
        sizes_after = []
        for quadrant, quadrant_data in data.items():
            for branchType, branchData in quadrant_data.items():
                if branchType == 'main_branch':
                    continue
                for key, value in branchData.items():
                    sizes_before.append(len(value))
        for quadrant, quadrant_data in data.items():
            for branchType, branch_data in quadrant_data.items():
                if branchType == 'main_branch':
                    continue
                metric_data = branch_data[metric_key]
                percentile_value = np.percentile(metric_data, percentile)
                indices = [i for i, x in enumerate(metric_data) if x > percentile_value]
                for key, value in branch_data.items():
                    new_values_from_indices = [value[i] for i in indices]
                    branch_data[key] = new_values_from_indices
        for quadrant, quadrant_data in data.items():
            for branchType, branchData in quadrant_data.items():
                if branchType == 'main_branch':
                    continue
                for key, value in branchData.items():
                    sizes_after.append(len(value))
        print(f"Before: {sizes_before}")
        print(f"After: {sizes_after}")
        if len(sizes_before) != len(sizes_after):
            print("ERROR: sizes before and after are not the same!")

        return data

    def visualize_metric(self, data, metric_key, percentiles):
        for quadrant, quadrant_data in data.items():
            for branchType, branch_data in quadrant_data.items():
                metric_data = branch_data[metric_key]
                mean = np.mean(metric_data)
                median = np.median(metric_data)
                std = np.std(metric_data)
                percentile_values = {p: np.percentile(metric_data, p) for p in percentiles}

                plt.hist(metric_data, bins=1000, alpha=0.5, label='Metric Counts')

                plt.axvline(mean, color='r', linestyle='dashed', linewidth=2, label=f'Mean: {mean:.2f}')
                plt.axvline(median, color='g', linestyle='dashed', linewidth=2, label=f'Median: {median:.2f}')
                plt.axvline(mean + std, color='purple', linestyle='dotted', linewidth=2, label=f'Std: {std:.2f}')

                for p, val in percentile_values.items():
                    plt.axvline(val, color=np.random.rand(3, ), linestyle='dashed', linewidth=2,
                                label=f'{p}th percentile: {val:.2f}')

                plt.title(f'Quadrant {quadrant} - {branchType} - {metric_key}')
                plt.xlabel('Metric values')
                plt.ylabel('Frequency')

                plt.legend()

                plt.show()

    def make_dataframe(self, data):
        flattened_data = []
        for quadrant, quadrant_data in data.items():
            for branchType, branch_data in quadrant_data.items():
                for metric, value in branch_data.items():
                    flattened_data.append({
                        'Quadrant': quadrant,
                        'BranchType': branchType,
                        'Metric': metric,
                        'Value': round(value, 2),  # rounding values
                    })
        df = pd.DataFrame(flattened_data)
        return df




    def process_data(self, data):
        new_data = {}
        for quadrant, quadrant_data in data.items():
            new_data[quadrant] = {}
            for branchType, branch_data in quadrant_data.items():
                new_data[quadrant][branchType] = {}
                for metric, metric_data in branch_data.items():
                    if metric == 'breakage_rates':
                        mean_breakage_rate = np.mean(metric_data)
                        print(f"Value of mean_breakage_rate: {mean_breakage_rate} is with length: {len(metric_data)}")
                        new_data[quadrant][branchType]['mean_breakage_rates'] = mean_breakage_rate
                    if metric == 'mean_resolution_times':
                        mean_resolution_times = np.mean(metric_data)
                        new_data[quadrant][branchType]['mean_resolution_times'] = mean_resolution_times
                    if metric == 'median_resolution_times':
                        median_resolution_times = np.median(metric_data)
                        new_data[quadrant][branchType]['median_resolution_times'] = median_resolution_times
                    if metric == 'mean_build_resolutions':
                        mean_build_resolutions = np.mean(metric_data)
                        new_data[quadrant][branchType]['mean_build_resolutions'] = mean_build_resolutions
                    if metric == 'median_build_resolutions':
                        median_build_resolutions = np.median(metric_data)
                        new_data[quadrant][branchType]['median_build_resolutions'] = median_build_resolutions
                    if metric == 'job_churns':
                        mean_job_churns = np.mean(metric_data)
                        new_data[quadrant][branchType]['mean_job_churns'] = mean_job_churns
                    if metric == 'runs_counts':
                        mean_runs_counts = np.mean(metric_data)
                        new_data[quadrant][branchType]['mean_runs_counts'] = mean_runs_counts

        # self.nice_print(new_data)

        output_json_data('./output/stats/quadrant_branches_processed3.json', new_data)

        return new_data

    def nice_print(self, data):
        for quadrant, quadrant_data in data.items():
            print(quadrant)
            for branch, branch_data in quadrant_data.items():
                print(branch)
                for metric, metric_data in branch_data.items():
                    print(metric)
                    print(metric_data)
                    print('---------------------')