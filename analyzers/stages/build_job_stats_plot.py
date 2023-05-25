import os
import json
import matplotlib.pyplot as plt
from analyzers.stages.stage import PipelineStage


class PlotStatistics(PipelineStage):
    def __init__(self, verbose=True):
        self.verbose = verbose

    def run(self, input):
        with open("./output/build_stats.json", 'r') as f:
            build_stats = json.load(f)

        for key, stats in build_stats.items():
            repo_name, workflow_name = key.split("_")

            if self.verbose:
                print(f'Processing {repo_name} / {workflow_name}')

            # Create a directory for this repository if it doesn't exist
            os.makedirs(os.path.join('output', repo_name), exist_ok=True)

            # Generate the plot
            plt.figure(figsize=(10, 6))

            # Plot build times with different colors for failures
            for i, build_time in enumerate(stats['build_times']):
                color = 'green'  # Default color for successful builds
                if i >= stats['successes']:
                    color = 'red'  # Color for failed builds
                plt.plot(i + 1, build_time, marker='o', markersize=5, color=color)

            # Add labels and title
            plt.title(f'Build times for {repo_name} / {workflow_name}')
            plt.xlabel('Build number')
            plt.ylabel('Build time (seconds)')

            # Add the statistics as text on the plot
            y_position = max(stats['build_times'])  # Place the statistics at the top of the plot
            plt.text(0, y_position, f"Average build time: {stats['average_build_time']:.2f}s")
            plt.text(0, y_position * 0.95, f"Success rate: {stats['success_rate']:.2f}%")
            plt.text(0, y_position * 0.90, f"Failure frequency: {stats['failure_frequency']}")
            plt.text(0, y_position * 0.85, f"Build flakiness: {stats['build_flakiness']:.2f}%")
            plt.text(0, y_position * 0.80, f"Performance score: {stats['performance_score']:.2f}")

            # Save the plot as a PNG image in the repository's directory
            plt.savefig(os.path.join('output', repo_name, f'{workflow_name}_build_times.png'))

            # Close the plot to free up memory
            plt.close()

        return input
