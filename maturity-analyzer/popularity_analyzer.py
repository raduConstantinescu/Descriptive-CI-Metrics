import datetime
import json

from repository_analyzer import RepositoryAnalyzer
from analyzer_exception import AnalyzerException
import matplotlib.pyplot as plt

class PopularityAnalyzer(RepositoryAnalyzer):

    def __init__(self, github, maturity_group, popularity_metric):
        self.github = github
        self.repositories = self.load_repository_data()
        self.maturity_group = maturity_group
        self.popularity_metric(popularity_metric)

    def analyze(self):
        if self.maturity_group in self.repositories.keys():
            self.popularity_metric_analyzer(self.popularity_metric)
        elif self.maturity_group == 'all':
            self.analyze_all(self.repositories, self.popularity_metric)
        else:
            raise AnalyzerException("not a maturity_group")

    def load_repository_data(self):
        repositories_data = {}
        with open('repository_lists/repositories.json', 'r') as f:
            repositories_data = json.load(f)
        print(repositories_data)
        return repositories_data

    def filter_repos_by_maturity_level(self, maturity_level):
        return self.repositories[maturity_level]

    def calculate_repo_ages(self, repos):
        current_date = datetime.datetime.now()
        repo_created_at = [repo['created_at'] for repo in repos]
        repo_ages = []

        for date in repo_created_at:
            date_obj = datetime.datetime.strptime(date, "%Y-%m-%d")
            age = current_date.year - date_obj.year

            if (current_date.month, current_date.day) < (date_obj.month, date_obj.day):
                age -= 1

            repo_ages.append(age)

        return repo_ages

    # {"name": "facebook/react", "created_at": "2013-05-24", "updated_at": "2023-05-31", "stargazers_count": 208285,
     # "watchers_count": 208285, "forks_count": 43514}
    def popularity_metric_analyzer(self, metric):
        repos = self.filter_repos_by_maturity_level(self.maturity_group)
        repo_names = [repo['name'] for repo in repos]
        repo_metric_count = [repo[metric] for repo in repos]
        repo_ages = self.calculate_repo_ages(repos)

        age_groups = self.group_repos_by_age(repo_names, repo_metric_count, repo_ages)
        average_count = self.calculate_average_counts(age_groups)

        self.plot_results(age_groups, average_count, metric)

    def analyze_all(self, repos, metric):
        repo_names = []
        repo_metric_count = []
        repo_ages = []
        for maturity, repositories in repos.items():
            for repo in repositories:
                repo_names.append(repo['name'])
                repo_metric_count.append(repo[metric])
            repo_ages.extend(self.calculate_repo_ages(repos[maturity]))

        age_groups = self.group_repos_by_age(repo_names, repo_metric_count, repo_ages)
        average_count = self.calculate_average_counts(age_groups)
        self.plot_results(age_groups, average_count, metric)

    def group_repos_by_age(self, repo_names, repo_metric_count, ages):
        age_groups = {}
        for name, scount, age in zip(repo_names, repo_metric_count, ages):
            if age in age_groups.keys():
                age_groups[age].append((name, scount))
            else:
                age_groups[age] = [(name, scount)]

        return age_groups

    def calculate_average_counts(self, age_groups):
        average_count = []
        sum = 0
        for age_group in age_groups:
            for item in age_groups[age_group]:
                sum += item[1]
            avg = sum / len(age_groups[age_group])
            average_count.append(avg)
            sum = 0

        return average_count

    def plot_results(self, x_axis, y_axis, metric):
        plt.bar(x_axis.keys(), y_axis)
        plt.xlabel('Age group')
        plt.ylabel(metric + ' average per age group')
        plt.title('Age Counter')
        plt.xticks(list(range(min(x_axis), max(x_axis) + 1)))
        plt.show()