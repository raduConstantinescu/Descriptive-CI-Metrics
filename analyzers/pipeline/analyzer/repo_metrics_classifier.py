from analyzers.pipeline.stage import PipelineStage
from ...utils import load_data
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
import numpy as np

class RepoMetricsClassifierConfig:
    def __init__(self, config):
        self.input_file = config["input_file"]
        self.ci_data = config["ci_data"]
        self.ci_stats = config["ci_stats"]

class RepoMetricsClassifier(PipelineStage):
    def __init__(self, args, config):
        self.verbose = args.verbose
        self.config = config

    # "average_execution_time": 1537.0287648054145,
    # "success_rate": 0.7834179357021996,
    # {
    #     "average_success_rate": 0.73783988558146,
    #     "median_success_rate": 0.8440358931552587,
    #     "average_execution_time": 11469.895653402207,
    #     "median_execution_time": 1521.1235058374123
    # }
    #
    def filter_by_ci_performance(self, ci_data, ci_stats):
        # do 4 quadrants or splits for each of the cases and append them to the corresponding ones
        filtered_workflows_by_performance = {}
        filtered_workflows_by_performance['low_execution_time_low_success_rate'] = []
        filtered_workflows_by_performance['high_execution_time_low_success_rate'] = []
        filtered_workflows_by_performance['low_execution_time_high_success_rate'] = []
        filtered_workflows_by_performance['high_execution_time_high_success_rate'] = []

        for repo_workflow_name, workflow_data in ci_data.items():
            if workflow_data['average_execution_time'] < ci_stats['average_execution_time'] and\
                    workflow_data['success_rate'] < ci_stats['average_success_rate']:
                filtered_workflows_by_performance['low_execution_time_low_success_rate'].append(repo_workflow_name)
            elif workflow_data['average_execution_time'] >= ci_stats['average_execution_time'] and\
                    workflow_data['success_rate'] < ci_stats['average_success_rate']:
                filtered_workflows_by_performance['high_execution_time_low_success_rate'].append(repo_workflow_name)
            elif workflow_data['average_execution_time'] < ci_stats['average_execution_time'] and\
                    workflow_data['success_rate'] >= ci_stats['average_success_rate']:
                filtered_workflows_by_performance['low_execution_time_high_success_rate'].append(repo_workflow_name)
            elif workflow_data['average_execution_time'] >= ci_stats['average_execution_time'] and\
                    workflow_data['success_rate'] >= ci_stats['average_success_rate']:
                filtered_workflows_by_performance['high_execution_time_high_success_rate'].append(repo_workflow_name)

        return filtered_workflows_by_performance


    def kclustering(self, ci_data):

        # Extract features from data into a list of feature vectors and keep track of names:
        feature_vectors = []
        workflow_names = []
        for workflow_name, workflow_data in ci_data.items():
            execution_time = workflow_data['average_execution_time']
            success_rate = workflow_data['success_rate']
            num_successes = workflow_data['conclusions'].get('success', 0)  # default to 0 if no 'success' key
            num_failures = workflow_data['conclusions'].get('failure', 0)  # default to 0 if no 'failure' key
            feature_vector = [execution_time, success_rate, num_successes, num_failures]
            feature_vectors.append(feature_vector)
            workflow_names.append(workflow_name)

        # Convert list of feature vectors into a numpy array:
        X = np.array(feature_vectors)

        # # Standardize the features to have zero mean and unit variance
        # scaler = StandardScaler()
        # X = scaler.fit_transform(X)

        # Run K-means clustering:

        kmeans = KMeans(n_clusters=4, random_state=0).fit(X)
        labels = kmeans.labels_
        self.plot_clusters(feature_vectors, labels)

    def plot_clusters(self, feature_vectors, labels):
        import matplotlib.pyplot as plt

        colors = ['b', 'g', 'r', 'c', 'm', 'y', 'k']

        # Convert feature vectors and labels to NumPy arrays
        feature_vectors = np.array(feature_vectors)
        labels = np.array(labels)

        # Create a scatter plot
        plt.figure(figsize=(10, 10))

        for i in range(max(labels) + 1):
            # Get all points in this cluster
            cluster_points = feature_vectors[labels == i]
            # Plot the points
            plt.scatter(cluster_points[:, 0], cluster_points[:, 1], c=colors[i % len(colors)], label=f'Cluster {i}')

        # Add legend and labels
        plt.legend()
        plt.xlabel('Average execution time')
        plt.ylabel('Success rate')
        plt.title('Workflow clusters')

        # Show the plot
        plt.show()

    def run(self):
        data = load_data(self.config.input_file)
        ci_data = load_data(self.config.ci_data)
        ci_stats = load_data(self.config.ci_stats)

        for repo in data:
            data[repo]['size'] /= 1024

        # In ci data we get information about the average execution time and success rate of each workflow


        # repos_by_language = self.classify_repos_by_language(data)
        # self.plot_repos_by_numeric_feature(data, 'commits', 'Number of Commits', 'Repositories by Number of Commits')
        # self.plot_repos_by_numeric_feature(data, 'contributors', 'Number of Contributors',
        #                            'Repositories by Number of Contributors')
        # self.plot_repos_by_numeric_feature(data, 'releases', 'Number of Releases', 'Repositories by Number of Releases')
        # self.plot_repos_by_numeric_feature(data, 'forks', 'Number of Forks', 'Repositories by Number of Forks')
        # self.plot_repos_by_numeric_feature(data, 'size', 'Size (MB)', 'Repositories by Size')
        # filtered_workflows_by_performance = self.filter_by_ci_performance(ci_data, ci_stats)
        # print(filtered_workflows_by_performance)
        #
        # for performance_type, repos in filtered_workflows_by_performance.items():
        #     print(f"Performance type: {performance_type} with {len(repos)} repos")

        self.kclustering(ci_data)

    def plot_repos_by_numeric_feature(self, data, feature, ylabel, title):
        values = [repo[feature] for repo in data.values()]
        repo_names = list(data.keys())
        mean_values = np.mean(values)
        median_values = np.median(values)

        plt.figure(figsize=(10, 5))
        plt.bar(repo_names, values)
        plt.axhline(mean_values, color='r', linestyle='dashed', linewidth=2, label=f'Mean: {mean_values:.2f}')
        plt.axhline(median_values, color='g', linestyle='dashed', linewidth=2, label=f'Median: {median_values:.2f}')
        plt.legend(loc='upper left')
        plt.xlabel('Repository')
        plt.ylabel(ylabel)
        plt.title(title)
        plt.xticks(rotation=45)
        plt.show()

    def classify_repos_by_language(self, data):
        language_repos = {}
        for repo_name, repo in data.items():
            if repo['language'] not in language_repos:
                language_repos[repo['language']] = [repo_name]
            else:
                language_repos[repo['language']].append(repo_name)

        if self.verbose:
            for language, repos in language_repos.items():
                print(f"Language: {language} with {len(repos)} repos")

        return language_repos

    def plot_repos_by_language(self, language_repos):
        languages = list(language_repos.keys())
        num_repos = [len(repos) for repos in language_repos.values()]

        plt.figure(figsize=(10, 5))
        plt.bar(languages, num_repos)
        plt.xlabel('Language')
        plt.ylabel('Number of Repositories')
        plt.title('Repositories by Language')
        plt.xticks(rotation=45)
        plt.show()


# details = {
#             'workflows': workflows,
#             'num_workflows': len(workflows),
#             'creation_date': repo_obj.created_at,
#             'is_fork': repo_obj.fork,
#             'forks': repo_obj.forks_count,
#             'language': repo_obj.language,
#             'languages': repo_obj.get_languages(),
#             'commits': repo_obj.get_commits().totalCount,
#             'contributors': repo_obj.get_contributors().totalCount,
#             'releases': repo_obj.get_releases().totalCount,
#             'size': repo_obj.size
#         }