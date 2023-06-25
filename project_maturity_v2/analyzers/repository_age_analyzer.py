import datetime
import matplotlib.pyplot as plt
import seaborn as sns

from project_maturity_v2.utils import extract_data_from_json


class AgeAnalyzer():
    def __init__(self):
        self.data = extract_data_from_json('../outputs_v2/repo_data.json')
        self.maturity_info = extract_data_from_json('../outputs_v2/repo_maturity.json')

    def analyze(self):
        mature_ages = []
        immature_ages = []
        for repo_name, repo_data in self.data.items():
            if repo_name not in self.maturity_info.keys():
                continue
            if self.maturity_info[repo_name] is True:
                mature_ages.append(self.calculate_age(repo_data["created_at"]))
            else:
                immature_ages.append(self.calculate_age(repo_data["created_at"]))

        self.plot_violin(mature_ages,immature_ages)
        # self.plot_kernel_density(mature_ages, immature_ages)

    def plot_violin(self, mature_ages, immature_ages):
        data = [mature_ages, immature_ages]

        # Create the violin plot
        plt.figure(figsize=(8, 6))
        parts = plt.violinplot(data, showmedians=True)

        colors = ['red', 'orange']  # Specify the colors here
        for pc, color in zip(parts['bodies'], colors):
            pc.set_facecolor(color)

        # Set labels and title
        plt.xlabel('Project Type')
        plt.ylabel('Age')
        plt.title('Distribution of Project Ages')

        # Set x-axis tick labels
        plt.xticks([1, 2], ['Mature projects', 'Immature projects'])
        plt.savefig('visualizations/violin_plot_ages')
        # Show the plot
        plt.show()


    def plot_kernel_density(self, mature_ages, immature_ages):

        # Create the kernel density plot
        plt.figure(figsize=(8, 6))
        sns.kdeplot(mature_ages, fill=True, label='Mature Projects')
        sns.kdeplot(immature_ages, fill=True, label='Immature Projects')

        # Set labels and title
        plt.xlabel('Age')
        plt.ylabel('Density')
        plt.title('Kernel Density Plot')

        # Show the plot
        plt.show()
        plt.savefig('visualizations/kernel_density_ages')

    def calculate_age(self, date):
        current_date = datetime.datetime.now()
        created_date = datetime.datetime.strptime(date, "%Y-%m-%dT%H:%M:%S")
        age = current_date.year - created_date.year

        if (current_date.month, current_date.day) < (created_date.month, created_date.day):
            age -= 1

        return age

AgeAnalyzer().analyze()