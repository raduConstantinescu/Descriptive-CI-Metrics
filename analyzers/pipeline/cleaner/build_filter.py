from analyzers.pipeline.stage import PipelineStage
from analyzers.utils import load_data, output_data



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
#                         "jobs": []
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


class BuildFilter(PipelineStage):
    def __init__(self, args):
        self.verbose = args.verbose
        self.filtered_workflows = 0
        self.filtered_runs = 0
        self.filtered_repos = 0

    def run(self):
        data = load_data('./new_output/filtered_data.json')

        # Using a copy of keys because we can't remove items from a dictionary during iteration
        for repo_name in list(data.keys()):
            data[repo_name]['workflows'] = [
                workflow for workflow in data[repo_name]['workflows']
                if self.filter_workflow(workflow)
            ]

            # If a repository has no workflows left, remove it
            if len(data[repo_name]['workflows']) == 0:
                del data[repo_name]
                self.filtered_repos += 1

            else:
                self.filtered_workflows += len(data[repo_name]['workflows'])

        # Saving filtered data
        output_data('./new_output/filtered_build_data.json', data)

        print(f"Filtered out {self.filtered_workflows} workflows")
        print(f"Filtered out {self.filtered_repos} repositories")


    def filter_workflow(self, workflow):
        # Iterate over workflow's runs
        workflow['runs'] = [
            run for run in workflow['runs']
            if self.filter_run(run)
        ]

        self.filtered_runs += len(workflow['runs'])

        # Return False if all runs are filtered out
        return len(workflow['runs']) > 0

    def filter_run(self, run):
        # If jobs exist in the run, filter them
        if run.get('jobs') is not None:
            run['jobs'] = [
                job for job in run['jobs']
                if self.filter_job(job)
            ]
        # If no jobs or jobs is None, make it an empty list
        else:
            run['jobs'] = []

        # Return False if all jobs are filtered out or there are no jobs
        return len(run.get('jobs', [])) > 0

    def filter_job(self, job):
        # Check job's name
        if 'build' in job['name'].lower():
            return True

        # Check job's steps
        for step in job['steps']:
            if 'build' in step['name'].lower():
                return True

        # If neither job's name nor any step's name contains 'build', filter out the job
        return False



