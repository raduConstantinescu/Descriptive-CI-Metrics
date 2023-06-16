import datetime
import matplotlib.pyplot as plt

from project_maturity.analyzers.repository_analyzer import RepositoryAnalyzer
from project_maturity.utils import extract_data_from_json, calculate_descriptive_statistics


class RepoAgeAnalyzer(RepositoryAnalyzer):
    def __init__(self):
        self.data = extract_data_from_json('../output/immature_repo_data.json')

    def analyze(self):
        self.analyze_repo_ages()

    def analyze_repo_ages(self):
        ages = []
        for repo_name, repo_data in self.data.items():
            repo_age = self.calculate_age(repo_data["created_at"])
            ages.append(repo_age)

        self.pie_plot_ages(ages)
        self.box_plot_ages(ages)

        calculate_descriptive_statistics(ages)


    def pie_plot_ages(self, ages):
        age_counts = {}
        total_count = len(ages)

        # Count the occurrences of each age
        for age in ages:
            age_counts[age] = age_counts.get(age, 0) + 1

        # Calculate the percentage for each age
        age_percentages = [(age, count / total_count * 100) for age, count in age_counts.items()]

        # Sort the age percentages in ascending order
        age_percentages.sort()

        # Extract the ages and percentages for plotting
        ages = [age for age, _ in age_percentages]
        percentages = [percentage for _, percentage in age_percentages]

        # Define pastel colors
        colors = ['#ffb3ba', '#ffdfba', '#ffffba', '#baffc9', '#bae1ff', '#dabaff', '#ffbacd', '#ffd8b3']

        # Define the wedge properties to adjust the slice size
        wedgeprops = {'linewidth': 1.5, 'edgecolor': 'white'}

        # Define a custom autopct function to prevent overlapping percentages
        def format_percentage(pct):
            return "{:.1f}%".format(pct) if pct > 3 else ""

        # Plotting the pie chart with pastel colors, adjusted slice size, and custom autopct function
        plt.figure(figsize=(8, 6))
        plt.pie(percentages, labels=ages, colors=colors, autopct=format_percentage, wedgeprops=wedgeprops)
        plt.title("Age Percentages")


        save_path = f'./output/immature_age_pie_plot_{datetime.datetime.now().strftime("%Y-%m-%d_%H-%M")}.png'
        # Save the plot as an image file
        plt.savefig(save_path)

    def box_plot_ages(self, ages):
        # Create figure and axis objects
        fig, ax = plt.subplots()

        # Create the box plot
        ax.boxplot(ages)

        # Customize the plot
        ax.set_xlabel('Age')
        ax.set_ylabel('Years')
        ax.set_title('Distribution of Repository Ages')
        ax.set_xticklabels(['All Repositories'])

        save_path = f'./output/immature_age_box_plot_{datetime.datetime.now().strftime("%Y-%m-%d_%H-%M")}.png'
        # Save the plot as an image file
        plt.savefig(save_path)

    def calculate_age(self, date):
        current_date = datetime.datetime.now()
        created_date = datetime.datetime.strptime(date, "%Y-%m-%dT%H:%M:%S")
        age = current_date.year - created_date.year

        if (current_date.month, current_date.day) < (created_date.month, created_date.day):
            age -= 1

        return age

RepoAgeAnalyzer().analyze()