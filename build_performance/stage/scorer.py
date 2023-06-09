import glob
import os
import yaml
import json
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd

def filter_workflows(results, average_score):
    # Filter the workflows below the average
    for repo_name, repo_data in results.items():
        repo_data[:] = [item for item in repo_data if item['score'] >= average_score]

    return results

def remove_outliers(data):
    Q1 = data.quantile(0.25)
    Q3 = data.quantile(0.75)
    IQR = Q3 - Q1
    data_filtered = data[~((data < (Q1 - 1.5 * IQR)) | (data > (Q3 + 1.5 * IQR)))]
    return data_filtered


def parse_yaml(filename):
    try:
        with open(filename, 'r') as file:
            data = yaml.safe_load(file)
            return data
    except Exception as e:
        print(f'Failed to parse {filename} due to {str(e)}')
        return None


def get_workflow_score(data, repo_name, score_counts):
    score = 0
    if 'name' in data.keys():
        score += score_workflow_title(data['name'])
        score_counts[repo_name] += 1
    if 'jobs' in data.keys():
        score += score_jobs(data['jobs'], repo_name, score_counts)
    return score

def score_jobs(jobs, repo_name, score_counts):
    score = 0
    for key, value in jobs.items():
        score += score_job_title(key)
        score_counts[repo_name] += 1
        if isinstance(value, dict):
            score += score_job_data(value, repo_name, score_counts)
    return score

def score_job_data(data, repo_name, score_counts):
    score = 0
    if 'steps' in data.keys():
        score += score_steps(data['steps'], repo_name, score_counts)
    return score

def score_steps(steps, repo_name, score_counts):
    score = 0
    for step in steps:
        if isinstance(step, dict):
            if 'run' in step.keys():
                score += score_run(step['run'])
                score_counts[repo_name] += 1
            if 'uses' in step.keys():
                score += score_reusable_actions(step['uses'])
                score_counts[repo_name] += 1
    return score


def score_run(run):
    build_keywords = {
        # # Installation commands
        # "npm install": 100,
        # "yarn install": 100,
        # "mvn install": 100,
        # "gradle install": 100,
        # "ant install": 100,
        #
        # # Compilation / transpiling
        # "tsc": 300,
        # "ts-node": 300,
        # "mvn compile": 300,
        # "ant compile": 300,
        #
        # # Running commands
        # "npm run": 200,
        # "yarn run": 200,
        # "npm ci": 200,

        # # Test commands
        # "npm test": 400,
        # "yarn test": 400,
        # "mvn test": 400,
        # "mvn clean test": 500,
        # "gradle test": 400,
        # "ant test": 400,

        # Build commands
        "npm build": 700,
        "yarn build": 700,
        "mvn package": 700,
        "mvn clean package": 800,
        "gradle build": 700,
        "ant build": 700,
        "pnpm build": 700,
        "pnpm run build": 800,
        "npm run build": 800,

        # # Clean commands
        # "mvn clean install": 150,
        # "gradle clean": 150,
        #
        # # Check commands
        # "gradle check": 250,
    }

    score = 0

    # Ensure that `run` is a string before using the `in` operator
    if isinstance(run, str):
        for keyword, value in build_keywords.items():
            if keyword in run:
                score += value

    return score

def score_reusable_actions(action_name):
    action_keywords = {
        # "actions/checkout": 100,
        # "actions/setup-node": 500,
        # "actions/setup-java": 500,
        # "actions/cache": 100,
        # "docker/build-push-action": 1000,
    }

    score = 0
    for keyword, value in action_keywords.items():
        if keyword in action_name:
            score += value
    return score

def score_job_title(job_title):
    if 'build' in job_title.lower():
        return 100
    else:
        return 0

def score_workflow_title(title):
    title = title.lower()
    keyword_scores = {
        # # Pre-build process keywords
        # "validate": 100,
        # "lint": 200,

        # Build process keywords
        "ci": 300,
        "build": 500,

        # # Testing related keywords
        # "test": 400,
        # "tests": 400,
        # "unit": 400,
        # "e2e": 400,
        # "coverage": 400,
        # "benchmark": 400,

        # # Post-build process keywords
        # "package": 600,
        # "check": 700,
    }
    score = 0
    for keyword, keyword_score in keyword_scores.items():
        if keyword in title:
            score += keyword_score
    return score

def filter_workflows_and_remove_empty_repos(results, threshold):
    """
    This function removes workflows from each repository with scores below the threshold.
    If this results in an empty repository, it also removes the repository.

    :param results: dictionary of repositories containing workflows and their scores
    :param threshold: score threshold to filter workflows
    :return: a tuple containing the filtered dictionary and the total number of remaining workflows
    """
    filtered_results = {}
    total_workflows = 0
    for repo_name, repo_data in results.items():
        repo_data[:] = [item for item in repo_data if item['score'] >= threshold]
        if repo_data:  # If the repository is not empty after filtering
            filtered_results[repo_name] = repo_data
            total_workflows += len(repo_data)
    return filtered_results, total_workflows


def visualize_scores(scores):
    fig, axs = plt.subplots(2)
    fig.set_size_inches(18.5, 10.5)
    sns.histplot(scores, kde=False, ax=axs[0])
    axs[0].set_title('Histogram of Workflow Scores')
    sns.boxplot(x=scores, ax=axs[1])
    axs[1].set_title('Boxplot of Workflow Scores')
    plt.show()


# Main starts here:
results = {}
scores = []
score_counts = {}

for filename in glob.glob(os.path.join('../../build_performance/output/workflows', '**/*.yml'), recursive=True):
    print(filename)
    repo_name = filename.split("/")[-2]
    score_counts[repo_name] = 0
    data = parse_yaml(filename)

    if data is not None:
        score = get_workflow_score(data, repo_name, score_counts)
        if score > 0:
            scores.append(score)

        # If repo name is not yet in results, add it with an empty list
        if repo_name not in results:
            results[repo_name] = []

        # Append a dictionary with workflow name and score to the list
        results[repo_name].append({
            'workflow_name': data['name'] if 'name' in data else "Unnamed",
            'score': score
        })

        print(f'Score for {filename}: {score}')
    else:
        print(f'Skipping score calculation for {filename}')

    print('------------------')

# Normalize scores
for repo_name, repo_data in results.items():
    for item in repo_data:
        if score_counts[repo_name] > 0:
            item['score'] /= score_counts[repo_name]
        else:
            item['score'] = 0

# Save results to JSON
with open('workflow_scores.json', 'w') as f:
    json.dump(results, f, indent=4)

# Calculate and print statistics
if scores:
    normalized_scores = [score / count for score, count in zip(scores, score_counts.values()) if count != 0]
    log_scores = np.log1p(scores)
    visualize_scores(normalized_scores)
    print(f"Average score: {np.mean(normalized_scores)}")
    print(f"Median score: {np.median(normalized_scores)}")
    print(f"Min score: {np.min(normalized_scores)}")
    print(f"Max score: {np.max(normalized_scores)}")
    print(f"Standard deviation: {np.std(normalized_scores)}")
else:
    print("No scores were calculated.")

average_score = np.mean(normalized_scores)
median_score = np.median(normalized_scores)

# Filter out workflows that have a score below the average
results_filtered = filter_workflows(results, average_score)

# Remove outliers
scores_df = pd.DataFrame(normalized_scores, columns=['score'])
scores_df_filtered = remove_outliers(scores_df)

# Get filtered scores
filtered_scores = scores_df_filtered['score'].tolist()

# Filter out workflows that have a score below the average and remove empty repositories
results_filtered, total_workflows = filter_workflows_and_remove_empty_repos(results, average_score)

# Print the remaining number of repos and workflows
print(f"Remaining number of repositories: {len(results_filtered)}")
print(f"Remaining number of workflows: {total_workflows}")

# Save results_filtered to JSON
with open('workflow_scores_filtered.json', 'w') as f:
    json.dump(results_filtered, f, indent=4)





