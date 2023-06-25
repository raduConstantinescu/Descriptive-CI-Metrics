import ast

from project_maturity_v2.utils import extract_data_from_json


class BasicFeaturesAnalyzer():
    def __init__(self):
        self.data = extract_data_from_json('../outputs_v2/repo_data.json')
        self.maturity_info = extract_data_from_json('../outputs_v2/repo_maturity.json')
        self.mature_repos, self.immature_repos = self.cluster_repostiories()


    def cluster_repostiories(self):
        mature_repos = {}
        immature_repos = {}
        for repo_name, repo_data in self.data.items():
            if repo_name not in self.maturity_info.keys():
                continue
            if self.maturity_info[repo_name] is True:
                mature_repos[repo_name] = repo_data
                mature_repos[repo_name]["weekly_code_frequency"] = ast.literal_eval(repo_data["weekly_code_frequency"])
                mature_repos[repo_name]["weekly_code_additions"] = ast.literal_eval(repo_data["weekly_code_additions"])
                mature_repos[repo_name]["weekly_code_deletions"] = ast.literal_eval(repo_data["weekly_code_deletions"])
                mature_repos[repo_name]["weekly_commit_count_last_year"] = ast.literal_eval(repo_data["weekly_commit_count_last_year"])
            else:
                immature_repos[repo_name] = repo_data
                immature_repos[repo_name]["weekly_code_frequency"] = ast.literal_eval(repo_data["weekly_code_frequency"])
                immature_repos[repo_name]["weekly_code_additions"] = ast.literal_eval(repo_data["weekly_code_additions"])
                immature_repos[repo_name]["weekly_code_deletions"] = ast.literal_eval(repo_data["weekly_code_deletions"])
                immature_repos[repo_name]["weekly_commit_count_last_year"] = ast.literal_eval(repo_data["weekly_commit_count_last_year"])

        return mature_repos, immature_repos

    def analyze(self):

        mature_count = len(self.mature_repos.keys())
        immature_count = len(self.immature_repos.keys())

        size_mature = 0
        have_wiki_mature = 0
        watchers_mature = 0
        open_issues_mature = 0
        commits_count_mature = 0
        all_pr_count_mature = 0
        open_pr_count_mature = 0
        for repo_name, repo_data in self.mature_repos.items():
            size_mature += repo_data['size']

            if repo_data['has_wiki']:
                have_wiki_mature +=1

            watchers_mature += repo_data['watchers_count']
            open_issues_mature += repo_data['open_issues_count']
            commits_count_mature += repo_data['commits_count']
            all_pr_count_mature += repo_data['all_pull_requests_count']
            open_pr_count_mature += repo_data['open_pull_requests_count']

        avg_size_mature = size_mature / mature_count
        avg_have_wiki_mature = (have_wiki_mature /mature_count)*100
        avg_watchers_mature = watchers_mature /mature_count
        avg_open_issues_mature = open_issues_mature /mature_count
        avg_commits_count_mature = commits_count_mature /mature_count
        avg_all_pr_count_mature = all_pr_count_mature/mature_count
        avg_open_pr_count_mature = open_pr_count_mature/mature_count

        print("Mature")
        print("Average Repo Size: {:.2f}".format(avg_size_mature))
        print("Average Have Wiki: {:.2f}".format(avg_have_wiki_mature))
        print("Average Watchers: {:.2f}".format(avg_watchers_mature))
        print("Average Open Issues: {:.2f}".format(avg_open_issues_mature))
        print("Average Commits Count: {:.2f}".format(avg_commits_count_mature))
        print("Average All PR Count: {:.2f}".format(avg_all_pr_count_mature))
        print("Average Open PR Count: {:.2f}".format(avg_open_pr_count_mature))


        size_immature = 0
        have_wiki_immature = 0
        watchers_immature = 0
        open_issues_immature = 0
        commits_count_immature = 0
        all_pr_count_immature = 0
        open_pr_count_immature = 0
        for repo_name, repo_data in self.immature_repos.items():
            size_immature += repo_data['size']

            if repo_data['has_wiki']:
                have_wiki_immature += 1

            watchers_immature += repo_data['watchers_count']
            open_issues_immature += repo_data['open_issues_count']
            commits_count_immature += repo_data['commits_count']
            all_pr_count_immature += repo_data['all_pull_requests_count']
            open_pr_count_immature += repo_data['open_pull_requests_count']

        avg_size_immature = size_immature/immature_count
        avg_have_wiki_immature = (have_wiki_immature/immature_count)*100
        avg_watchers_immature = watchers_immature/immature_count
        avg_open_issues_immature = open_issues_immature/immature_count
        avg_commits_count_immature = commits_count_immature/immature_count
        avg_all_pr_count_immature = all_pr_count_immature/immature_count
        avg_open_pr_count_immature = open_pr_count_immature/immature_count

        print("\n Immature")
        print("Average Size (Immature): {:.2f}".format(avg_size_immature))
        print("Average Have Wiki (Immature): {:.2f}".format(avg_have_wiki_immature))
        print("Average Watchers (Immature): {:.2f}".format(avg_watchers_immature))
        print("Average Open Issues (Immature): {:.2f}".format(avg_open_issues_immature))
        print("Average Commits Count (Immature): {:.2f}".format(avg_commits_count_immature))
        print("Average All PR Count (Immature): {:.2f}".format(avg_all_pr_count_immature))
        print("Average Open PR Count (Immature): {:.2f}".format(avg_open_pr_count_immature))

BasicFeaturesAnalyzer().analyze()
