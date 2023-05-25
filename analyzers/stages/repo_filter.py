import os
import json
import re
import pandas as pd
from dateutil.parser import parse
from datetime import datetime, timedelta
from collections import defaultdict

from matplotlib import pyplot as plt

from analyzers.stages.stage import PipelineStage

class RepoFilter(PipelineStage):
    def __init__(self, filter_fn=None, verbose=True):
        if filter_fn is None:
            self.filter_fn = self.has_ci_workflow
        else:
            self.filter_fn = filter_fn
        self.verbose = verbose

    def run(self, input):
        with open('./output/workflows1.json', 'r') as f:
            data = json.load(f)

        filtered_data = {}
        language_counts = defaultdict(int)

        for repo, details in data.items():
            creation_date = parse(details['creation_date'])
            four_months_ago = datetime.now() - timedelta(days=120)
            if creation_date < four_months_ago and details['contributors'] >= 10 and details['commits'] >= 100 and \
                    details['num_workflows'] > 0:
                # Filter the workflows within the repository
                filtered_workflows = list(filter(self.filter_fn, details['workflows']))

                # Only keep repositories with at least one workflow left
                if filtered_workflows:
                    details['workflows'] = filtered_workflows
                    filtered_data[repo] = details
                    if details['language']:
                        language_counts[details['language']] += 1

        os.makedirs('./output', exist_ok=True)
        output_path = os.path.join('./output', 'filtered_repos.json')
        with open(output_path, 'w') as f:
            json.dump(filtered_data, f, indent=4)

        if self.verbose:
            print(f'Total repositories: {len(data)}')
            print(f'Filtered repositories: {len(filtered_data)}')
            print('Language percentages:')
            for language, count in language_counts.items():
                print(f'{language}: {count / len(filtered_data) * 100:.2f}%')

            self.plot_languages2(language_counts)

        return output_path

    @staticmethod
    def has_ci_workflow(workflow):
        ci_keywords = ["CI", "Continuous Integration", "Build", "Test", "Pipeline", "Deploy", "Release", "PR", "Lint"]
        pattern = re.compile("|".join(ci_keywords), re.IGNORECASE)
        return bool(pattern.search(workflow['name']))

    def plot_languages(self, language_counts):
        df = pd.DataFrame(list(language_counts.items()), columns=['Language', 'Count'])
        df.sort_values('Count', inplace=True, ascending=False)

        plt.figure(figsize=(12, 8))
        plt.barh(df['Language'], df['Count'], color='skyblue')
        plt.xlabel('Number of Repositories')
        plt.title('Programming Languages in Filtered Repositories')
        plt.show()

    def plot_languages2(self, language_counts):
        df = pd.DataFrame(list(language_counts.items()), columns=['Language', 'Count'])
        df.sort_values('Count', inplace=True, ascending=False)

        fig, ax = plt.subplots(figsize=(10, 10))
        wedges, labels, autopct = ax.pie(df['Count'], labels=df['Language'], autopct='%1.1f%%')

        ax.set_title('Programming Languages in Filtered Repositories', fontsize=25, fontweight='bold')

        # Increase the size of the labels and make them bold
        plt.setp(labels, fontsize=17, fontweight='bold')
        plt.setp(autopct, fontsize=15)  # Optionally, you can also change the font size of the percentages.

        plt.show()
