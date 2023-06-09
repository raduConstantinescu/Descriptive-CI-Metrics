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


for filename in glob.glob(os.path.join('../../../build_performance/output/workflows', '**/*.yml'), recursive=True):
    data = parse_yaml(filename)
    if data is not None and 'name' in data:
        workflow_name = data['name']
        workflow_occurrences[workflow_name] += 1

# Sort workflow names by occurrences in descending order
sorted_workflow_occurrences = dict(sorted(workflow_occurrences.items(), key=lambda item: item[1], reverse=True))

# Move workflows with keywords to the top
keywords = ['CI', 'build', 'test', 'release']  # Update with relevant keywords
keyword_workflows = {}
other_workflows = {}
for workflow, occurrences in sorted_workflow_occurrences.items():
    if any(keyword.lower() in workflow.lower() for keyword in keywords):
        keyword_workflows[workflow] = occurrences
    else:
        other_workflows[workflow] = occurrences

# Combine keyword workflows and other workflows
final_workflow_occurrences = {**keyword_workflows, **other_workflows}

# Output workflow names and occurrences to a JSON file
with open('./workflow_occurrences_output.json', 'w') as json_file:
    json.dump(final_workflow_occurrences, json_file, indent=4)