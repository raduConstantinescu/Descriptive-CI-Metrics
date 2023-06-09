import os
import glob
import yaml
import json
from collections import Counter

def parse_yaml(filename):
    with open(filename, 'r') as file:
        try:
            data = yaml.safe_load(file)
        except yaml.YAMLError as exc:
            print(f'Failed to parse {filename} due to {exc}')
            return None
    return data

workflow_occurrences = Counter()

for filename in glob.glob(os.path.join('../../build_performance/output/workflows', '**/*.yml'), recursive=True):
    data = parse_yaml(filename)
    if data is not None and 'name' in data:
        workflow_name = data['name']
        workflow_occurrences[workflow_name] += 1

# Group together similar keywords in workflow names
grouped_occurrences = Counter()
for workflow, occurrences in workflow_occurrences.items():
    keywords = workflow.lower().split()
    for i in range(len(keywords)):
        for j in range(i+1, len(keywords)+1):
            grouped_keyword = ' '.join(keywords[i:j])
            grouped_occurrences[grouped_keyword] += occurrences

# Filter grouped occurrences by minimum occurrence threshold
filtered_grouped_occurrences = {keyword: occurrences for keyword, occurrences in grouped_occurrences.items() if occurrences >= 10}

# Sort grouped occurrences by total occurrences in descending order
sorted_grouped_occurrences = dict(sorted(filtered_grouped_occurrences.items(), key=lambda item: item[1], reverse=True))

# Output grouped keyword occurrences to a JSON file
with open('./scorer_helpers/grouped_keyword_occurrences_output.json', 'w') as json_file:
    json.dump(sorted_grouped_occurrences, json_file, indent=4)
