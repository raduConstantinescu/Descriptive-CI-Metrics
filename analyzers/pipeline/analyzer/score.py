import yaml

# Define the common keywords
keywords = ['build', 'test', 'ci', 'compile', 'install']

# Load the YAML file
with open('../../new_output/workflows/apache_dubbo/build-and-test-scheduled-3.1.yml') as file:
    workflow = yaml.safe_load(file)

# Start the score
score = 0

# Check the name of the workflow
for keyword in keywords:
    if keyword in workflow.get('name', '').lower():
        score += 1

# Check the jobs of the workflow
for job in workflow.get('jobs', {}).values():
    for step in job.get('steps', []):
        for keyword in keywords:
            if keyword in step.get('name', '').lower():
                score += 1
            if keyword in str(step.get('run', '')).lower():
                score += 1

print(f"Score for the workflow: {score}")
