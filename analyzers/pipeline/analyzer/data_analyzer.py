import json
import statistics
from datetime import datetime

from analyzers.pipeline.stage import PipelineStage

# REPO = {
#             'workflows': workflows,
#             'num_workflows': len(workflows),
#             'creation_date': repo_obj.created_at,
#             'is_fork': repo_obj.fork,
#             'forks': repo_obj.forks_count,
#             'language': repo_obj.language,
#             'languages': repo_obj.get_languages(),
#             'commits': repo_obj.get_commits().totalCount,
#             'contributors': repo_obj.get_contributors().totalCount,
#             'releases': repo_obj.get_releases().totalCount,
#             'size': repo_obj.size
#         }

#
# WORKFLOW = {
#             'id': workflow.id,
#             'name': workflow.name,
#             'created_at': workflow.created_at,
#             'updated_at': workflow.updated_at,
#             'runs_count': workflow.get_runs().totalCount
#         }

# WORKFLOW RUN = {
#                         "id": run.id,
#                         "status": run.status,
#                         "conclusion": run.conclusion,
#                         "created_at": run.created_at,
#                         "updated_at": run.updated_at,
#                     }


# JOB INFO = {
#                             "id": job.get("id", ""),
#                             "status": job.get("status", ""),
#                             "conclusion": job.get("conclusion", ""),
#                             "started_at": job.get("started_at", ""),
#                             "completed_at": job.get("completed_at", ""),
#                             "name": job.get("name", ""),
#                             "steps": job.get("steps", [])
#                         }



# STEPS OF JOB: [
#                                     {
#                                         "name": "Set up job",
#                                         "status": "completed",
#                                         "conclusion": "success",
#                                         "number": 1,
#                                         "started_at": "2023-05-31T12:43:33.000+02:00",
#                                         "completed_at": "2023-05-31T12:43:34.000+02:00"
#                                     },

class CIAnalyzer(PipelineStage):
    def __init__(self, args):
        self.verbose = args.verbose

    def run(self):
        # I want to load data from a json file
        data = self._load_data()
        ci_data = {}

        # Iterate over each repository
        for repo_name, repo in data.items():
            # Iterate over each workflow
            for workflow in repo['workflows']:
                total_time = 0
                conclusions = {}
                workflow_runs = []

                # Iterate over each run
                for run in workflow['runs']:
                    # Calculate total execution time
                    created_at = datetime.strptime(run['created_at'], '%Y-%m-%d %H:%M:%S')
                    updated_at = datetime.strptime(run['updated_at'], '%Y-%m-%d %H:%M:%S')
                    execution_time = (updated_at - created_at).total_seconds()
                    total_time += execution_time

                    # Count conclusion types
                    if run['conclusion'] in conclusions:
                        conclusions[run['conclusion']] += 1
                    else:
                        conclusions[run['conclusion']] = 1

                    # Append workflow run data to the list
                    workflow_runs.append({
                        'created_at': run['created_at'],
                        'execution_time': execution_time,
                        'conclusion': run['conclusion']
                    })

                average_time = total_time/len(workflow['runs'])

                # Calculate success rate for successful conclusions
                success_rate = conclusions.get('success', 0) / sum(conclusions.values())

                # Construct the key as "reponame-workflowname-id"
                key = f"{repo_name}-{workflow['name']}-{workflow['id']}"

                # Add metrics and workflow runs to the data structure
                ci_data[key] = {
                    'average_execution_time': average_time,
                    'success_rate': success_rate,
                    'conclusions': conclusions,
                    'workflow_runs': workflow_runs
                }

        success_rates = []
        exec_times = []
        for repo_name, repo in data.items():
            for workflow in repo['workflows']:
                key = f"{repo_name}-{workflow['name']}-{workflow['id']}"
                success_rates.append(ci_data[key]['success_rate'])
                exec_times.append(ci_data[key]['average_execution_time'])

        print(f"Average success rate: {sum(success_rates)/len(success_rates)}")
        print(f"Average execution time: {sum(exec_times)/len(exec_times)}")
        print(f"Median success rate: {statistics.median(success_rates)}")
        print(f"Median execution time: {statistics.median(exec_times)}")

        # lets create a new dictonary with the average success rate and average execution time

        overall_stats = {
            'average_success_rate': sum(success_rates) / len(success_rates),
            'median_success_rate': statistics.median(success_rates),
            'average_execution_time': sum(exec_times) / len(exec_times),
            'median_execution_time': statistics.median(exec_times)
        }

        # save stats to json file
        with open('./new_output/overall_stats.json', 'w') as f:
            json.dump(overall_stats, f, indent=4)

        # Write the ci_data dictionary to a new JSON file
        with open('./new_output/ci_analysis.json', 'w') as f:
            json.dump(ci_data, f, indent=4)



    def _load_data(self):
        with open('./new_output/filtered_build_data.json') as json_file:
            data = json.load(json_file)
        return data