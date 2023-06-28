"""Analyzes activity around a release date"""
import json
import math
from datetime import datetime, timedelta

import matplotlib.pyplot as plt
import numpy as np


def date_counts(section):
    """
    Groups a list of dates together into a dictionary. The key is the date and the value is the
    amount of times the date occurred in the list
    """

    count = {}

    for date_str in section:
        date = datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
        day = date.date()
        if day in count:
            count[day] += 1
        else:
            count[day] = 1

    return count


def list_of_dates(start_date, end_date):
    "Generates a list of dates, starting from start_date and ending at end_date"

    return [start_date + timedelta(days=i) for i in range((end_date - start_date).days + 1)]


if __name__ == '__main__':
    with open('../result.json', encoding="utf-8") as file:
        data = json.load(file)

    SPREAD = 8  # The maximum amount of days to diverge from the release date to check activity minus 1
    commit_increases = [[] for _ in range(SPREAD)]  # The commit increases for every diverge
    for entry in data:
        if "commits" not in entry or "releases" not in entry:
            print(entry['repo'])
            continue
        date_counts_commits = date_counts(entry['commits']['dates'])
        date_counts_releases = date_counts(entry['releases']['dates'])

        date_counts_commits_copy = date_counts_commits.copy()
        days_in_interval = set()
        for i in range(0, SPREAD):
            if i == 0:
                for d in entry['releases']['dates']:
                    d = datetime.strptime(d, "%Y-%m-%d %H:%M:%S").date()
                    if d in date_counts_commits_copy:
                        del date_counts_commits_copy[d]
                    days_in_interval.add(d)

                avg_commits_in_interval = np.sum(list(
                    {key: date_counts_commits[key] for key in date_counts_commits.keys() -
                     date_counts_commits_copy.keys()}.values())) / len(days_in_interval)
                avg_commits_outside_interval = np.mean(list(date_counts_commits_copy.values()))

                commit_increases[i].append(avg_commits_in_interval / avg_commits_outside_interval)
            else:
                for d in entry['releases']['dates']:
                    d = datetime.strptime(d, "%Y-%m-%d %H:%M:%S").date()
                    day_before = d - timedelta(days=i)
                    day_after = d + timedelta(days=i)

                    days_in_interval.add(day_before)
                    days_in_interval.add(day_after)

                    if day_before in date_counts_commits_copy:
                        del date_counts_commits_copy[day_before]

                    if day_after in date_counts_commits_copy:
                        del date_counts_commits_copy[day_after]

                avg_commits_in_interval = np.sum(list(
                    {key: date_counts_commits[key] for key in date_counts_commits.keys() -
                     date_counts_commits_copy.keys()}.values())) / len(days_in_interval)
                avg_commits_outside_interval = np.mean(list(date_counts_commits_copy.values()))

                commit_increases[i].append(avg_commits_in_interval / avg_commits_outside_interval)

    # After getting all the data, plot the results
    for i, increase_commits in enumerate(commit_increases):
        bins = list(range(math.ceil(max(increase_commits)) + 1))
        plt.hist(increase_commits, bins=bins, edgecolor='black')

        print(f'day {i} percentage bigger than 1', (len([num for num in increase_commits if num >= 1]) / len(increase_commits)) * 100)
        print(f'day {i} percentage bigger than 2', (len([num for num in increase_commits if num >= 2]) / len(increase_commits)) * 100)

        plt.xlabel('Increase in commits')
        plt.ylabel('Amount of repositories')
        plt.title(f'Histogram of data with {i} days')
        plt.xticks(bins)
        plt.show()
