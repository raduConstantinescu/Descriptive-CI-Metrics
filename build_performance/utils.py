import json

import yaml


def load_json_data(path: object) -> object:
    with open(path) as f:
        data = json.load(f)
    return data


def output_json_data(path, data):
    with open(path, 'w') as f:
        json.dump(data, f, indent=4)
    return

def load_lines_from_file(path):
    lines = []
    with open(path, 'r') as file:
        for line in file:
            lines.append(line.strip())
    return lines

def write_lines_to_file(lines, path):
    with open(path, 'a') as file:
        for line in lines:
            file.write(line + '\n')

def parse_yaml(filename):
    try:
        with open(filename, 'r') as file:
            data = yaml.safe_load(file)
            return data
    except Exception as e:
        print(f'Failed to parse {filename} due to {str(e)}')
        return None
