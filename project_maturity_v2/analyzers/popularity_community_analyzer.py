from project_maturity_v2.utils import extract_data_from_json

import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt


class PopularityCommunityAnalyzer():
    def __init__(self):
        self.data = extract_data_from_json('../outputs_v2/repo_data.json')
        self.maturity_info = extract_data_from_json('../outputs_v2/repo_maturity.json')

    def analyze(self):
        repo_list = []

        # Iterate over the data and extract the relevant information
        for repo_name, repo_info in self.data.items():
            if repo_name in self.maturity_info.keys():
                maturity = self.maturity_info[repo_name]
                repo_info['maturity'] = maturity
                repo_list.append(repo_info)

        # Create a DataFrame from the repository list
        df = pd.DataFrame(repo_list)

        # Select the relevant columns for correlation analysis
        metrics = ['stargazers_count', 'forks_count', 'contributors_count', 'watchers_count']
        mature_metrics = df[df['maturity'] == True][metrics]
        immature_metrics = df[df['maturity'] == False][metrics]

        # Calculate the correlation matrices
        mature_corr = mature_metrics.corr()
        immature_corr = immature_metrics.corr()

        # Format the correlation matrices in BibTeX format
        mature_corr_bibtex = mature_corr.to_latex(index=True, header=True)
        immature_corr_bibtex = immature_corr.to_latex(index=True, header=True)

        # Print the correlation matrices in BibTeX format
        print("Correlation Matrix - Mature Repositories (BibTeX format):")
        print(mature_corr_bibtex)
        print()

        print("Correlation Matrix - Immature Repositories (BibTeX format):")
        print(immature_corr_bibtex)
        print()
        # Visualize the correlation matrices using heatmaps
        fig, axs = plt.subplots(1, 2, figsize=(12, 6))

        sns.heatmap(mature_corr, annot=True, cmap='seismic', ax=axs[0])
        axs[0].set_title('Correlation Matrix - Mature Repositories')

        sns.heatmap(immature_corr, annot=True, cmap='seismic', ax=axs[1])
        axs[1].set_title('Correlation Matrix - Immature Repositories')

        plt.tight_layout()
        plt.show()

    def plot_metrics(self):
        mature_stars_sum = 0
        mature_projects_count = 0
        mature_contributors_count = 0
        mature_forks_count = 0

        immature_stars_sum = 0
        immature_projects_count = 0
        immature_contributors_count = 0
        immature_forks_count = 0
        for repo_name, repo_data in self.data.items():
            if repo_name not in self.maturity_info.keys():
                continue

            if self.maturity_info[repo_name] is True:
                mature_projects_count += 1
                mature_stars_sum += repo_data['stargazers_count']
                mature_forks_count += repo_data['forks_count']
                mature_contributors_count += repo_data['contributors_count']
            else:
                immature_projects_count += 1
                immature_stars_sum += repo_data['stargazers_count']
                immature_forks_count += repo_data['forks_count']
                immature_contributors_count += repo_data['contributors_count']

        # Group labels
        labels = ['Average Stars', 'Contributors', 'Forks']

        # Data for mature and immature projects
        mature_data = [mature_stars_sum / mature_projects_count, mature_contributors_count / mature_projects_count, mature_forks_count / mature_projects_count]
        immature_data = [immature_stars_sum / immature_projects_count, immature_contributors_count / immature_projects_count, immature_forks_count / immature_projects_count]

        print("Mature data:")
        print("Average number of stars:", mature_data[0])
        print("Average number of contributors:", mature_data[1])
        print("Average number of forks:", mature_data[2])

        print("\nImmature data:")
        print("Average number of stars:", immature_data[0])
        print("Average number of contributors:", immature_data[1])
        print("Average number of forks:", immature_data[2])

        # Position of each group on x-axis
        x = np.arange(len(labels))

        # Width of each bar
        width = 0.35

        # Create the bar plot
        fig, ax = plt.subplots()
        rects1 = ax.bar(x - width / 2, mature_data, width, label='Mature Projects', color='#297373')
        rects2 = ax.bar(x + width / 2, immature_data, width, label='Immature Projects', color='#5DD39E')

        # Add labels, title, and legend
        ax.set_ylabel('Average Value')
        ax.set_title('Average Number of Stars, Contributors, and Watchers')
        ax.set_xticks(x)
        ax.set_xticklabels(labels)
        # Move the legend to the upper right corner
        ax.legend(loc='upper center')
        plt.savefig('visualizations/stars_watchers_contributors')
        plt.show()



PopularityCommunityAnalyzer().plot_metrics()