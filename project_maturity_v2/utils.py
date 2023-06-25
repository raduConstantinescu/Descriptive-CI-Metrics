import json
import os

import numpy as np


def load_repos(path):
    repo_list = []
    with open(path, 'r') as file:
        for line in file:
            # Remove leading/trailing whitespace and newline characters
            repo_name = line.strip()
            repo_list.append(repo_name)
    return repo_list

def was_repo_processed(repo_name, path):
        with open(path, 'r') as file:
            for line in file:
                if line.strip() == repo_name:
                    return True
        return False

def save_processed(repo, path):
    with open(path, 'a') as file:
        file.write(repo + '\n')

def save_data(key, value, path):
    data = {}

    if os.path.exists(path) and os.path.getsize(path) > 0:
        with open(path, 'r') as file:
            data = json.load(file)  # Load existing JSON data

    if 'weekly_code_frequency' in value:
        value['weekly_code_frequency'] = json.dumps(value['weekly_code_frequency'])

    if 'weekly_code_additions' in value:
        value['weekly_code_additions'] = json.dumps(value['weekly_code_additions'])

    if 'weekly_code_deletions' in value:
        value['weekly_code_deletions'] = json.dumps(value['weekly_code_deletions'])

    if 'weekly_commit_count_last_year' in value:
        value['weekly_commit_count_last_year'] = json.dumps(value['weekly_commit_count_last_year'])

    data[key] = value  # Add the new key-value pair

    with open(path, 'w') as file:
        json.dump(data, file, indent=4)  # Write updated data back to the JSON file

def extract_data_from_json(json_file_path):
    with open(json_file_path) as file:
        data = json.load(file)
    return data

def calculate_descriptive_statistics(values):
    # Calculate descriptive statistics
    mean = np.mean(values)  # Mean
    median = np.median(values)  # Median
    std = np.std(values)  # Standard deviation
    min_age = np.min(values)  # Minimum age
    max_age = np.max(values)  # Maximum age

    print("Mean:", mean)
    print("Median:", median)
    print("Standard Deviation:", std)
    print("Minimum Age:", min_age)
    print("Maximum Age:", max_age)

def save_filtered(repo_name, is_mature, path):
    data = {}

    # Check if the JSON file exists and is non-empty
    if os.path.exists(path) and os.path.getsize(path) > 0:
        with open(path, "r") as json_file:
            try:
                data = json.load(json_file)
            except json.JSONDecodeError:
                pass

    # Add new key-value pair to the dictionary
    data[repo_name] = is_mature

    # Save the updated data to the JSON file
    with open(path, "w") as json_file:
        json.dump(data, json_file, indent=4)
        json_file.write("\n")
