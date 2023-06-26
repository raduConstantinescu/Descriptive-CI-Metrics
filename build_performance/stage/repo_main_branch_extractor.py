from build_performance.stage.stage import PipelineStage
from build_performance.utils import load_json_data, output_json_data


class RepoMainBranchExtractor(PipelineStage):
    def __init__(self, github):
        self.github = github

    def run(self):
        print("RepoMainBranchExtractor")
        build_performance_data = load_json_data('./output/stats/build_performance_with_cache.json')
        for repoName, workflows in build_performance_data.items():
            repo = self.github.get_repo(repoName)
            main_branch = repo.get_branch(repo.default_branch)
            for workflowName, workflowData in workflows.items():
                workflowData['metrics']['main_branch'] = main_branch.name
        output_json_data('./output/stats/build_performance_with_main_branch.json', build_performance_data)