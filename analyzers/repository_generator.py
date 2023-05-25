from github import Github
from dotenv import load_dotenv
import os
load_dotenv()
token = os.getenv('GITHUB_ACCESS_TOKEN')

# Initialize a Github instance with your access token
g = Github(token)

# Define an empty list of excluded repositories
excluded_repos = []

# Read the repos.txt file and add the repositories to the excluded_repos list
with open('../repos.txt', 'r') as file:
    for line in file:
        excluded_repos.append(line.strip())

# Search for repositories
repos = g.search_repositories(query='Rust', sort='updated')

# Create an empty list to store the results
random_repos = []

for repo in repos:
    # Skip if the repository is in the excluded list
    if repo.full_name in excluded_repos:
        continue

    random_repos.append(repo.full_name)

    # Stop when we have 100 repositories
    if len(random_repos) == 100:
        break

# Append the list of random repositories to the repos.txt file
with open('../repos.txt', 'a') as file:
    for repo in random_repos:
        file.write(repo + '\n')
