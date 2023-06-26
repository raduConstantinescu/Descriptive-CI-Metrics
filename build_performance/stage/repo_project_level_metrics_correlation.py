from datetime import datetime
import pandas as pd
import numpy as np
from dateutil.relativedelta import relativedelta
import matplotlib.pyplot as plt
import seaborn as sns
from pandas.plotting import parallel_coordinates

from build_performance.stage.stage import PipelineStage
from build_performance.utils import load_json_data, output_json_data


class RepoProjectLevelMetricsCorrelationAnalysis(PipelineStage):
    def __init__(self):
        pass

    def run(self):
        data = load_json_data('./output/stats/build_performance_with_main_branch_runs.json')
        workflows_metrics_by_quadrant = {}

        overall_metrics = {
            'commits': [],
            'branches': [],
            'releases': [],
            'contributors': [],
            'stars': [],
            'forks': [],
            'size': [],
            'age_in_months': [],
        }

        for repoName, repoData in data.items():
            for workflowName, workflowData in repoData.items():
                quadrant = workflowData['quadrant']
                if quadrant not in workflows_metrics_by_quadrant:
                    workflows_metrics_by_quadrant[quadrant] = {
                        'commits': [],
                        'branches': [],
                        'releases': [],
                        'contributors': [],
                        'stars': [],
                        'forks': [],
                        'size': [],
                        'age_in_months': [],
                    }
                workflows_metrics_by_quadrant[quadrant]['commits'].append(workflowData['metrics']['commits'])
                workflows_metrics_by_quadrant[quadrant]['branches'].append(workflowData['metrics']['branches'])
                workflows_metrics_by_quadrant[quadrant]['releases'].append(workflowData['metrics']['releases'])
                workflows_metrics_by_quadrant[quadrant]['contributors'].append(workflowData['metrics']['contributors'])
                workflows_metrics_by_quadrant[quadrant]['stars'].append(workflowData['metrics']['stars'])
                workflows_metrics_by_quadrant[quadrant]['forks'].append(workflowData['metrics']['forks'])
                workflows_metrics_by_quadrant[quadrant]['size'].append(workflowData['metrics']['size'])
                created_at = workflowData['metrics']['created_at']
                created_at_datetime = datetime.strptime(created_at, '%Y-%m-%dT%H:%M:%S')
                current_datetime = datetime.now()
                rd = relativedelta(current_datetime, created_at_datetime)
                project_age_in_months = rd.years * 12 + rd.months
                workflows_metrics_by_quadrant[quadrant]['age_in_months'].append(project_age_in_months)

                # aggregating metrics for overall correlation
                overall_metrics['commits'].append(workflowData['metrics']['commits'])
                overall_metrics['branches'].append(workflowData['metrics']['branches'])
                overall_metrics['releases'].append(workflowData['metrics']['releases'])
                overall_metrics['contributors'].append(workflowData['metrics']['contributors'])
                overall_metrics['stars'].append(workflowData['metrics']['stars'])
                overall_metrics['forks'].append(workflowData['metrics']['forks'])
                overall_metrics['size'].append(workflowData['metrics']['size'])
                overall_metrics['age_in_months'].append(project_age_in_months)

        workflow_stats_by_quadrant = {}

        for quadrant, metrics in workflows_metrics_by_quadrant.items():
            workflow_stats_by_quadrant[quadrant] = {
                'commits': np.mean(metrics['commits']),
                'branches': np.mean(metrics['branches']),
                'releases': np.mean(metrics['releases']),
                'contributors': np.mean(metrics['contributors']),
                'stars': np.mean(metrics['stars']),
                'forks': np.mean(metrics['forks']),
                'size': np.mean(metrics['size']) / 1024,
                'age_in_months': np.mean(metrics['age_in_months']),
            }

        for quadrant, metrics in workflow_stats_by_quadrant.items():
            workflow_stats_by_quadrant[quadrant] = {
                'commits': round(metrics['commits'], 2),
                'branches': round(metrics['branches'], 2),
                'releases': round(metrics['releases'], 2),
                'contributors': round(metrics['contributors'], 2),
                'stars': round(metrics['stars'], 2),
                'forks': round(metrics['forks'], 2),
                'size': round(metrics['size'], 2),
                'age_in_months': round(metrics['age_in_months'], 2),
            }

        print(workflow_stats_by_quadrant)
        output_json_data('./output/stats/workflow_stats_by_quadrant.json', workflow_stats_by_quadrant)

        correlation_by_quadrant = {}

        for quadrant, metrics in workflows_metrics_by_quadrant.items():
            df = pd.DataFrame(metrics)
            corr = df.corr()

            correlation_by_quadrant[quadrant] = corr.to_dict()

            plt.figure(figsize=(10, 8))
            sns.heatmap(corr, xticklabels=corr.columns, yticklabels=corr.columns, annot=True)
            plt.title(f'Correlation Heatmap for Quadrant: {quadrant}')
            plt.savefig(f'./output/stats/correlation_heatmap_{quadrant}.png')

        print(correlation_by_quadrant)

        # calculating correlation for overall data
        overall_df = pd.DataFrame(overall_metrics)
        overall_corr = overall_df.corr()
        correlation_by_quadrant['overall'] = overall_corr.to_dict()

        plt.figure(figsize=(10, 8))
        sns.heatmap(overall_corr, xticklabels=overall_corr.columns, yticklabels=overall_corr.columns, annot=True)
        plt.title(f'Correlation Heatmap for Overall Data')
        plt.savefig(f'./output/stats/correlation_heatmap_overall.png')

        print(correlation_by_quadrant)

        output_json_data('./output/stats/correlation_by_quadrant.json', correlation_by_quadrant)

        workflow_stats_df = pd.DataFrame(workflow_stats_by_quadrant).transpose()
        workflow_stats_df.rename(index={'LBLT': 'LBLD', 'LBHT': 'LBHD', 'HBHT': 'HBHD', 'HBLT': 'HBLD'}, inplace=True)
        workflow_stats_df_normalized = (workflow_stats_df - workflow_stats_df.min()) / (
                    workflow_stats_df.max() - workflow_stats_df.min())
        workflow_stats_df_normalized['Quadrant'] = workflow_stats_df_normalized.index

        color_map = {'LBLD': 'green', 'HBHD': 'red', 'LBHD': 'orange', 'HBLD': 'coral'}
        for quadrant in workflow_stats_df_normalized['Quadrant'].unique():
            if quadrant not in color_map:
                color_map[quadrant] = 'gray'

        plt.figure(figsize=(10, 8))
        parallel_coordinates(workflow_stats_df_normalized, 'Quadrant',
                             color=[color_map.get(x) for x in workflow_stats_df_normalized['Quadrant']], linewidth=3)
        plt.title('Normalized Parallel Coordinates Plot for Project Level Metrics', fontdict={'fontsize': 16})
        plt.xticks(rotation=15)
        plt.tick_params(axis='x', which='major', labelsize=14)
        plt.tick_params(axis='y', which='major', labelsize=14)
        plt.grid(True)
        plt.legend(prop={'size': 12}, loc='upper right')

        plt.savefig('./output/stats/parallel_coordinates_plot.png')
        plt.show()

        workflow_stats_by_quadrant = load_json_data('./output/stats/workflow_stats_by_quadrant.json')

        differences = pairwise_difference(workflow_stats_by_quadrant)
        z_scores = calculate_z_scores(differences)
        grouped = group_similar(z_scores)

        for metric, pairs in grouped.items():
            print(f"{metric}: {pairs}")



def pairwise_difference(data):
    """
    Calculate pairwise differences for each metric between quadrants.
    """
    differences = {}
    quadrants = list(data.keys())
    for i in range(len(quadrants)):
        for j in range(i + 1, len(quadrants)):
            q1 = quadrants[i]
            q2 = quadrants[j]
            pair = f"{q1}-{q2}"
            differences[pair] = {metric: abs(data[q1][metric] - data[q2][metric]) for metric in data[q1].keys()}
    return differences

def calculate_z_scores(data):
    """
    Calculate z-scores for the differences.
    """
    flattened = [value for sublist in data.values() for value in sublist.values()]
    mean = np.mean(flattened)
    std_dev = np.std(flattened)
    z_scores = {pair: {metric: (value - mean) / std_dev for metric, value in pair_data.items()} for pair, pair_data
                in data.items()}
    return z_scores

def group_similar(data, threshold=0.3):
    """
    Group metrics that have similar z-scores.
    """
    grouped = {}
    for pair, pair_data in data.items():
        for metric, z_score in pair_data.items():
            if abs(z_score) < threshold:
                if metric not in grouped:
                    grouped[metric] = []
                grouped[metric].append(pair)
    return grouped













