import argparse
import json
import os
import time

from dotenv import load_dotenv
from github import Github

from analyzers.pipeline.analyzer.ci_plotter import CIPlotter, CIPlotterConfig
from analyzers.pipeline.analyzer.ci_analyzer import CIAnalyzer, CIAnalyzerConfig
from analyzers.pipeline.analyzer.ci_quadran_plotter import CIQuadrantPlotter, CIQuadrantPlotterConfig
from analyzers.pipeline.cleaner.build_filter import BuildFilter
from analyzers.pipeline.cleaner.data_cleaner import CIFilter
from analyzers.pipeline.cleaner.json_merge import JsonMergeStage, JsonMergeConfig
from analyzers.pipeline.cleaner.repo_filter import RepoWorkflowBuildFilter, RepoWorkflowBuildFilterConfig
from analyzers.pipeline.extractor.job_extractor import JobExtractor
from analyzers.pipeline.repo_generator import RepoGenerator, RepoGeneratorConfig
from analyzers.pipeline.extractor.repo_metrics_extractor import RepoMetricsExtractor
from analyzers.pipeline.extractor.repo_workflow_runs_extractor import WorkflowRunExtractor


def main():
    parser = argparse.ArgumentParser(description='CI Build Performance Analyzer.')
    parser.add_argument('-v', '--verbose', action='store_true', help='increase output verbosity')
    parser.add_argument('-s', '--stats', action='store_true', help='print stats about the pipeline stage')
    parser.add_argument('-stage', '--stage', type=int, help='run a specific stage in the pipeline')
    parser.add_argument('-start', '--start', type=int, help='start from a specific repo')
    parser.add_argument('-analyze', '--analyze', action='store_true', help='analyze the data')
    args = parser.parse_args()
    args.verbose = True

    g, config_data = setup()
    pipeline = [
        RepoGenerator(g, args, RepoGeneratorConfig(config_data["RepoGenerator"])),
        RepoMetricsExtractor(g, args),
        WorkflowRunExtractor(g, args),
        JobExtractor(g, args)
    ]

    data_cleaning_pipeline = [
        # RepoWorkflowBuildFilter(args, RepoWorkflowBuildFilterConfig(config_data["RepoWorkflowBuildFilter"])),
        JsonMergeStage(args, JsonMergeConfig(config_data["JsonMergeStage"])),
    ]

    analyzer_pipeline = [
        # CIAnalyzer(args, CIAnalyzerConfig(config_data["CIAnalyzer"])),
        # CIPlotter(args, CIPlotterConfig(config_data["CIPlotter"])),
        CIQuadrantPlotter(args, CIQuadrantPlotterConfig(config_data["CIQuadrantPlotter"]))
    ]

    if args.analyze:
        pipeline = []

    if args.stage:
        pipeline = [pipeline[args.stage]]

    for stage in analyzer_pipeline:
        if args.verbose:
            print(f"Running {stage.__class__.__name__} stage...")
        start_time = time.time()
        start_remaining = g.get_rate_limit().core.remaining
        stage.run()
        end_time = time.time()
        end_remaining = g.get_rate_limit().core.remaining
        execution_time = end_time - start_time
        used_requests = start_remaining - end_remaining
        if args.verbose:
            print(f"Output saved to {input}")
            print(f"Execution time for {stage.__class__.__name__}: {execution_time} seconds")
            print(f"API requests used for {stage.__class__.__name__}: {used_requests}")
            print(f"API requests remaining: {end_remaining}")

    print("Done!")

def setup():
    load_dotenv()
    g = Github(os.getenv('GITHUB_ACCESS_TOKEN'))
    with open('config.json') as f:
        config_data = json.load(f)
    return g, config_data


if __name__ == '__main__':
    main()
