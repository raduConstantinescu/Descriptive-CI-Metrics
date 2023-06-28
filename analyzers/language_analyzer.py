"""Analyzes language metric"""
import json

import numpy as np

if __name__ == '__main__':
    with open('../result.json', encoding="utf-8") as file:
        data = json.load(file)

    repository_by_language = {}

    for entry in data:
        main_language = entry['language']['main_language']

        if main_language in repository_by_language:
            repository_by_language[main_language].append(entry)
        else:
            repository_by_language[main_language] = [entry]

    for language, repositories in repository_by_language.items():
        print(language, "Amount of repositories:", len(repositories))
        print("Average amount of commits", np.mean([repo['commits']['count'] for repo in repositories]))
        print("Average amount of closed pull requests", np.mean([repo['pull_requests']['count_closed'] for repo in repositories]))
        print("Average amount of contributors", np.mean([repo['contributors']['count'] for repo in repositories]))
        print("Average amount of issues", np.mean([repo['issues']['count'] for repo in repositories]))
        print("Average amount of releases", np.mean([repo['releases']['count'] for repo in repositories]))
        print()
