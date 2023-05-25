import json
import matplotlib.pyplot as plt

# Load the data
with open('./output/build_stats.json', 'r') as f:
    data = json.load(f)

# Extract performance scores
performance_scores = {repo: details['performance_score'] for repo, details in data.items()}

# Categorize the repositories based on performance scores
categories = {
    'low': [],
    'medium': [],
    'high': []
}

for repo, score in performance_scores.items():
    if score < 0.50:  # These thresholds are just examples and can be adjusted
        categories['low'].append(repo)
    elif score < 0.75:
        categories['medium'].append(repo)
    else:
        categories['high'].append(repo)

# Plot the distribution of performance scores
plt.hist(performance_scores.values(), bins=20, edgecolor='black')
plt.title('Distribution of Performance Scores', fontsize=16, fontweight='bold')
plt.xlabel('Performance Score', fontsize=14, fontweight='bold')
plt.ylabel('Number of Repositories', fontsize=14, fontweight='bold')
plt.xticks(fontsize=12)
plt.yticks(fontsize=12)
plt.show()
