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

def gather_runs(data):
    runs = []
    if 'jobs' in data:
        for job in data['jobs'].values():
            if 'steps' in job:
                for step in job['steps']:
                    if 'run' in step:
                        runs.append(step['run'])
    return runs

runs_counter = Counter()

for filename in glob.glob(os.path.join('../../../build_performance/output/workflows', '**/*.yml'), recursive=True):
    data = parse_yaml(filename)
    if data is not None:
        runs = gather_runs(data)
        runs_counter.update(runs)

# Filter runs that are used more than 5 times
filtered_runs = {run: count for run, count in runs_counter.items() if count > 12}

# Output filtered runs sorted by the number of occurrences to a JSON file
with open('./filtered_runs_output.json', 'w') as json_file:
    json.dump(dict(sorted(filtered_runs.items(), key=lambda item: item[1], reverse=True)), json_file, indent=4)
