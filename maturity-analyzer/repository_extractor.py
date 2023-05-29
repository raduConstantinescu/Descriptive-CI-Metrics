import datetime
import time
from enum import Enum

import requests

class ClusterProperties(Enum):
    MATURE = "mature", 10, 15, 6
    MIDDLE = "middle", 5, 10, 3
    IMMATURE = "immature", 0, 5, 1

class RepositoryExtractor:
    def __init__(self, access_token, cluster_parameters = ClusterProperties.MATURE):
        self.access_token = access_token
        self.cluster_parameters = cluster_parameters.value

    def extract_repos(self):
        headers = {'Authorization': f'Bearer {self.access_token}'}

        cluster_name = self.cluster_parameters[0]
        older_than = self.cluster_parameters[1]
        print(older_than)
        younger_than = self.cluster_parameters[2]
        print(younger_than)

        older_than_years = (datetime.datetime.now() - datetime.timedelta(days=365 * older_than))\
            .strftime("%Y-%m-%d")
        younger_than_years = (datetime.datetime.now() - datetime.timedelta(days=365 * younger_than)) \
            .strftime("%Y-%m-%d")

        print(younger_than_years)
        print(older_than_years)

        total_repos = 1000  # Number of repositories to retrieve
        repos_per_page = 100  # Number of repositories per page
        current_page = 1
        repo_list = []

        while len(repo_list) < total_repos:
            # Define the search query parameters
            params = {
                'q': f'created:{younger_than_years}..{older_than_years}',
                'sort': 'updated',
                'order': 'desc',
                'per_page': repos_per_page,
                'page': current_page
            }

            # Send the API request
            response = requests.get('https://api.github.com/search/repositories', headers=headers, params=params)

            # Check rate limit status
            remaining = int(response.headers.get('X-RateLimit-Remaining', 0))
            reset_time = int(response.headers.get('X-RateLimit-Reset', 0))

            if remaining == 0:
                # Sleep until rate limit reset time
                sleep_duration = reset_time - time.time()
                print(f"Rate limit exceeded. Sleeping for {sleep_duration} seconds.")
                time.sleep(sleep_duration)
                continue

            # Parse the JSON response
            data = response.json()

            # Extract owner/name of each repository
            repo_list.extend(['{}/{}'.format(item['owner']['login'], item['name']) for item in data['items']])

            # If the total number of repositories is already reached, break the loop
            if len(repo_list) >= total_repos:
                break

            # Move to the next page
            current_page += 1

        # Write the repository list to a file
        with open(f'raw_repository_lists/repository_list_HELLOOOOO.txt', 'w') as file:
            file.write('\n'.join(repo_list))

        return self