import numpy as np

from build_performance.stage.stage import PipelineStage
from build_performance.utils import load_json_data
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd


class RepoDayOfWeekAnalysis(PipelineStage):
    def __init__(self):
        pass

    def run(self):
        data = load_json_data('./output/stats/build_performance_with_ff.json')

        jobs_quadrant = {}
        dow_quadrant = {}
        for repoName, repoData in data.items():
            for workflowName, workflowData in repoData.items():
                quadrant = workflowData['quadrant']
                if quadrant not in dow_quadrant:
                    dow_quadrant[quadrant] = {}
                    dow_quadrant[quadrant]['Monday'] = 0
                    dow_quadrant[quadrant]['Tuesday'] = 0
                    dow_quadrant[quadrant]['Wednesday'] = 0
                    dow_quadrant[quadrant]['Thursday'] = 0
                    dow_quadrant[quadrant]['Friday'] = 0
                    dow_quadrant[quadrant]['Saturday'] = 0
                    dow_quadrant[quadrant]['Sunday'] = 0
                    jobs_quadrant[quadrant] = []
                jobs_quadrant[quadrant].append(workflowData['jobs_count'])
                max_day_count = 0
                max_day = ''
                for day, dayData in workflowData['days_of_week'].items():
                    if dayData['total'] > max_day_count:
                        max_day_count = dayData['total']
                        max_day = day
                dow_quadrant[quadrant][max_day] += 1

        for quadrant, quadrantData in dow_quadrant.items():
            print('# Quadrant ' + str(quadrant) + ' most common day of the week is ' + str(max(quadrantData, key=quadrantData.get)) + ' with ' + str(quadrantData[max(quadrantData, key=quadrantData.get)]) + ' runs')

        print(dow_quadrant)

        dow_quadrant_percentages = {}
        for quadrant, quadrantData in dow_quadrant.items():
            dow_quadrant_percentages[quadrant] = {}
            for day, dayData in quadrantData.items():
                dow_quadrant_percentages[quadrant][day] = np.round_(dayData/sum(quadrantData.values()),2)*100

        print(dow_quadrant_percentages)

        print("Job quadrants belows")
        for quadrant, quadrantData in jobs_quadrant.items():
            jobs_quadrant[quadrant] = {}
            jobs_quadrant[quadrant]['average'] = np.round(np.mean(quadrantData),2)
            jobs_quadrant[quadrant]['median'] = np.round(np.median(quadrantData),2)
            jobs_quadrant[quadrant]['p80'] = np.round(np.percentile(quadrantData, 80),2)
            jobs_quadrant[quadrant]['p95'] = np.round(np.percentile(quadrantData, 95),2)
            jobs_quadrant[quadrant]['p99'] = np.round(np.percentile(quadrantData, 99),2)


        print(jobs_quadrant)
        data = dow_quadrant_percentages

        df = pd.DataFrame(data).reset_index().melt(id_vars='index', var_name='Quadrant', value_name='Runs')
        plt.figure(figsize=(12, 6))

        preference_order = ['LBLT', 'LBHT', 'HBLT', 'HBHT']

        df['Quadrant'] = pd.Categorical(df['Quadrant'], categories=preference_order, ordered=True)

        df.sort_values('Quadrant')

        name_mapping = {'LBLT': 'LBLD', 'LBHT': 'LBHD', 'HBLT': 'HBLD', 'HBHT': 'HBHD'}

        # Heatmap
        plt.figure(figsize=(8, 6))

        heatmap_data = pd.DataFrame(data)
        heatmap_data.rename(columns=name_mapping, inplace=True)  # Rename for the heatmap as well
        sns.heatmap(heatmap_data, annot=True, fmt=".2f")
        plt.xlabel('Quadrant')
        plt.ylabel('Day of the Week')
        plt.title('Heatmap of Dominant Activity Day of the Week / Quadrant')
        plt.savefig('./output/stats/heatmap_dow_quadrant.png')
        plt.show()







