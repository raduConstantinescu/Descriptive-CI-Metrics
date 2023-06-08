import json

def load_json_data(path):
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
