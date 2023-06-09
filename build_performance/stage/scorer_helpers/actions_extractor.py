import glob
import yaml
import json
import os
from collections import defaultdict

def parse_yaml(filename):
    try:
        with open(filename, 'r') as file:
            data = yaml.safe_load(file)
        return data
    except Exception as e:
        print(f"Failed to parse {filename} due to {str(e)}")
        return None

def gather_actions(data, action_counter):
    if data is None:
        return action_counter

    if 'jobs' in data.keys():
        for job in data['jobs'].values():
            if 'steps' in job.keys():
                for step in job['steps']:
                    if 'uses' in step.keys():
                        action_counter[step['uses']] += 1
    return action_counter

def main():
    action_counter = defaultdict(int)

    for filename in glob.glob(os.path.join('../../build_performance/output/workflows', '**/*.yml'), recursive=True):
        data = parse_yaml(filename)
        action_counter = gather_actions(data, action_counter)

    sorted_action_counter = dict(sorted(action_counter.items(), key=lambda item: item[1], reverse=True))

    filtered_actions = {action: count for action, count in sorted_action_counter.items() if count > 5}

    with open('./scorer_helpers/actions.json', 'w') as json_file:
        json.dump(filtered_actions, json_file, indent=4)

if __name__ == "__main__":
    main()
