from project_maturity.utils import extract_data_from_json, save_data
from project_maturity_v2.analyzers.code_frequency_analyzer import CodeFrequencyAnalyzer


class RepositoryFilter():
    def __init__(self):
        self.file_data = extract_data_from_json('outputs_v2/file_count.json')
        self.repo_data = extract_data_from_json('outputs_v2/repo_data.json')
        self.code_frequency_analyzer = CodeFrequencyAnalyzer()

    def filter(self):
        print(f"We analyze {len(self.file_data.keys())} repositories")
        have_ci = 0
        no_ci = 0
        have_files = 0
        not_enough_files = 0
        good_code_freq = 0
        bad_code_freq = 0
        mature = 0
        immature = 0
        for repo_name in self.file_data.keys():
            check_ci = self.check_ci(repo_name)
            check_file_count = self.check_file_count(repo_name)
            check_code_frequency = self.code_frequency_analyzer.analyze(repo_name)

            if check_ci and check_file_count and check_code_frequency:
                mature += 1
                value = {"mature": True, "cause": None}
                save_data(repo_name, value, 'outputs_v2/repo_maturity.json')
                continue

            elif check_ci:
                if check_code_frequency:
                    value = {"mature": False, "cause": "files"}
                    save_data(repo_name, value, 'outputs_v2/repo_maturity.json')
                elif check_file_count:
                    value = {"mature": False, "cause": "code"}
                    save_data(repo_name, value, 'outputs_v2/repo_maturity.json')
                else:
                    value = {"mature": False, "cause": "code and files"}
                    save_data(repo_name, value, 'outputs_v2/repo_maturity.json')

            elif check_file_count:
                if check_ci:
                    value = {"mature": False, "cause": "code"}
                    save_data(repo_name, value, 'outputs_v2/repo_maturity.json')
                elif check_code_frequency:
                    value = {"mature": False, "cause": "ci"}
                    save_data(repo_name, value, 'outputs_v2/repo_maturity.json')
                else:
                    value = {"mature": False, "cause": "ci and files"}
                    save_data(repo_name, value, 'outputs_v2/repo_maturity.json')

            elif check_code_frequency:
                if check_ci:
                    value = {"mature": False, "cause": "files"}
                    save_data(repo_name, value, 'outputs_v2/repo_maturity.json')
                elif check_file_count:
                    value = {"mature": False, "cause": "ci"}
                    save_data(repo_name, value, 'outputs_v2/repo_maturity.json')
                else:
                    value = {"mature": False, "cause": "ci and code"}
                    save_data(repo_name, value, 'outputs_v2/repo_maturity.json')


        print(f"Out of the analyzed repositories {have_ci} have CI implemented and {no_ci} don't.")
        print(f"Out of the analyzed repositories {have_files} have at least 500 files and {not_enough_files} don't.")
        print(f"Out of the analyzed repositories {good_code_freq} have good code frequency and {bad_code_freq} don't.")
        print(f"Out of the analyzed repositories {mature} are considered mature, and {immature} are considered immature.")


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