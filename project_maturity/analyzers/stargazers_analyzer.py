import numpy as np
from scipy import stats
import statsmodels.api as sm
import matplotlib.pyplot as plt

# Example data
from project_maturity.analyzers.repository_analyzer import RepositoryAnalyzer
from project_maturity.utils import extract_data_from_json


class StargazersAnalyzer(RepositoryAnalyzer):
    def __init__(self):
        self.mature_repos = extract_data_from_json('../output/repo_data.json')
        self.immature_repos = extract_data_from_json('../output/immature_repo_data.json')

    def analyze(self):
        mature_stargazers = []
        for repo_name, repo_data in self.mature_repos.items():
            mature_stargazers.append(repo_data["stargazers_count"])

        immature_stargazers = []
        for repo_name, repo_data in self.mature_repos.items():
            immature_stargazers.append(repo_data["stargazers_count"])

        print("T TEST")
        self.t_test_calculate(mature_stargazers, immature_stargazers)

        print("U TEST")
        self.u_test_calculate(mature_stargazers, immature_stargazers)

        print("LINEAR REGRESSION")
        self.linear_regression_calculate(mature_stargazers, immature_stargazers)


    def t_test_calculate(self, mature_repos, immature_repos):
        # T-Test
        t_statistic, p_value = stats.ttest_ind(mature_repos, immature_repos, equal_var=False)
        print(f"T-Test: t-statistic = {t_statistic}, p-value = {p_value}")

    def u_test_calculate(self, mature_repos, immature_repos):
        # Mann-Whitney U Test
        u_statistic, p_value = stats.mannwhitneyu(mature_repos, immature_repos, alternative='two-sided')
        print(f"Mann-Whitney U Test: U-statistic = {u_statistic}, p-value = {p_value}")

    def linear_regression_calculate(self, mature_repos, immature_repos):
        # Linear Regression
        y = np.array(mature_repos + immature_repos)
        x = np.array([1] * len(mature_repos) + [0] * len(immature_repos))
        x = sm.add_constant(x)  # Adding constant term for the intercept

        model = sm.OLS(y, x)
        results = model.fit()

        print("Linear Regression:")
        print(results.summary())

        plt.scatter(x, y)
        plt.plot(x, results.predict(), color='red', linewidth=2)
        plt.xlabel('Project Maturity')
        plt.ylabel('Stargazers Count')
        plt.title('Linear Regression: Project Maturity vs. Stargazers Count')
        plt.show()


    def box_plot(self, mature_projects, immature_projects):
        # Box plot
        data = [mature_projects, immature_projects]
        labels = ['Mature Projects', 'Immature Projects']
        plt.boxplot(data, labels=labels)
        plt.xlabel('Project Maturity')
        plt.ylabel('Stargazers Count')
        plt.title('Comparison of Stargazers Count')
        plt.show()

    def violin_plot(self, mature_projects, immature_projects):
        # Violin plot
        data = [mature_projects, immature_projects]
        labels = ['Mature Projects', 'Immature Projects']
        plt.violinplot(data, showmedians=True, showextrema=True)
        plt.xticks([1, 2], labels)
        plt.xlabel('Project Maturity')
        plt.ylabel('Stargazers Count')
        plt.title('Comparison of Stargazers Count')
        plt.show()

StargazersAnalyzer().analyze()