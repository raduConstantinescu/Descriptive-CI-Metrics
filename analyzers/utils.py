import json

def load_data(path):
    with open(path) as f:
        data = json.load(f)
    return data

def output_data(path, data):
    with open(path, 'w') as f:
        json.dump(data, f, indent=4)
    return