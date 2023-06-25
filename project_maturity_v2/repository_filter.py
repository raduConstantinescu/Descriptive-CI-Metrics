from project_maturity_v2.utils import extract_data_from_json, save_filtered
from project_maturity_v2.analyzers.code_frequency_analyzer import CodeFrequencyAnalyzer
import matplotlib.pyplot as plt
import numpy as np


class RepositoryFilter():
    def __init__(self):
        self.file_data = extract_data_from_json('outputs_v2/file_count.json')
        self.repo_data = extract_data_from_json('outputs_v2/repo_data.json')
        self.code_frequency_analyzer = CodeFrequencyAnalyzer()

    def filter(self):
        # print(f"We analyze {len(self.file_data.keys())} repositories")
        # ci_implemented = 0
        # ci_not_implemented = 0
        # files_gt_500 = 0
        # files_lt_500 = 0
        # good_code_freq = 0
        # bad_code_freq = 0
        # mature = 0
        # immature = 0

        repos_with_ci = []
        for repo_name in self.file_data.keys():
            check_ci = self.check_ci(repo_name)

            if check_ci:
                repos_with_ci.append(repo_name)
            else:
                save_filtered(repo_name, False, 'outputs_v2/repo_maturity.json')

        repos_with_files_gt_500 = []
        for repo_name in repos_with_ci:
            check_file_count = self.check_file_count(repo_name)

            if check_file_count:
                repos_with_files_gt_500.append(repo_name)
            else:
                save_filtered(repo_name, False, 'outputs_v2/repo_maturity.json')

        mature_repos = []
        for repo_name in repos_with_files_gt_500:
            check_code_frequency = self.code_frequency_analyzer.analyze(repo_name)
            if check_code_frequency:
                mature_repos.append(repo_name)
            else:
                save_filtered(repo_name, False, 'outputs_v2/repo_maturity.json')


        for repo_name in mature_repos:
            save_filtered(repo_name, True, 'outputs_v2/repo_maturity.json')

        print(f'{len(repos_with_ci)} left after first filter')
        print(f'{len(repos_with_files_gt_500)} left after second filter')
        print(f'{len(mature_repos)} fount mature')

        #     
        #
        #
        #
        #     check_file_count = self.check_file_count(repo_name)
        #     check_code_frequency = self.code_frequency_analyzer.analyze(repo_name)
        #
        #
        #
        #     if check_ci and check_file_count and check_code_frequency:
        #         mature += 1
        #         save_filtered(repo_name, True, 'outputs_v2/repo_maturity.json')
        #     else:
        #         immature +=1
        #         save_filtered(repo_name, False, 'outputs_v2/repo_maturity.json')
        #
        #     if check_ci:
        #         ci_implemented+=1
        #     else:
        #         ci_not_implemented+=1
        #
        #     if check_file_count:
        #         files_gt_500+=1
        #     else:
        #         files_lt_500+=1
        #
        #     if check_code_frequency:
        #         good_code_freq+=1
        #     else:
        #         bad_code_freq+=1
        #
        #
        #
        # print(f"Out of the analyzed repositories {ci_implemented} have CI implemented and {ci_not_implemented} don't.")
        # print(f"Out of the analyzed repositories {files_gt_500} have at least 500 files and {files_lt_500} don't.")
        # print(f"Out of the analyzed repositories {good_code_freq} have good code frequency and {bad_code_freq} don't.")
        # print(f"Out of the analyzed repositories {mature} are considered mature, and {immature} are considered immature.")
        #
        # # Define the color palette
        # colors = ['#ff9999', '#66b3ff', '#99ff99', '#ffcc99']
        #
        # # Create a figure with three subplots
        # fig, axes = plt.subplots(1, 3, figsize=(9, 3))
        #
        # # Plot the CI implementation
        # labels_ci = ['CI Implemented\n', 'CI Not\n Implemented\n']
        # axes[0].pie([ci_implemented, ci_not_implemented], labels=labels_ci, autopct='%1.1f%%', colors=colors)
        # axes[0].set_title('CI Implementation')
        #
        # # Plot the file count
        # labels_files = ['Files > 500\n', 'Files < 500\n']
        # axes[1].pie([files_gt_500, files_lt_500], labels=labels_files, autopct='%1.1f%%', colors=colors)
        # axes[1].set_title('File Count')
        #
        # # Plot the code frequency
        # labels_code = ['Good Code\nFrequency\n', 'Bad Code\nFrequency\n']
        # axes[2].pie([good_code_freq, bad_code_freq], labels=labels_code, autopct='%1.1f%%', colors=colors)
        # axes[2].set_title('Code Frequency')
        #
        # # Set an aspect ratio for a circular pie
        # axes[0].set_aspect('equal')
        # axes[1].set_aspect('equal')
        # axes[2].set_aspect('equal')
        #
        # # Add a common title for all subplots
        # plt.suptitle('Repository Filters')
        #
        # # Adjust the spacing between subplots
        # plt.tight_layout()
        #
        # # Show the plot
        # plt.show()

    def check_ci(self, repo_name):
        repo_data = self.file_data[repo_name]
        if repo_data["ci_files"] > 0:
            return True
        return False

    def check_file_count(self, repo_name):
        repo_data = self.file_data[repo_name]
        if repo_data["files_count"] >= 500:
            return True
        return False


RepositoryFilter().filter()