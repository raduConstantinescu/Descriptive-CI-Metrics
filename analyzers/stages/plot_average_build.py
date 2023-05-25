import json
import os
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime
from analyzers.stages.stage import PipelineStage

class VisualizeStatistics(PipelineStage):
    def __init__(self, verbose=True):
        self.verbose = verbose

    def run(self, input_file_path):
        # Load statistics from the input file
        # input_file_path = "./output/build_stats.json"
        with open(input_file_path, 'r') as f:
            stats = json.load(f)

        # Ensure the 'plots' directory exists
        plots_dir = 'plots'
        os.makedirs(plots_dir, exist_ok=True)

        # Iterate over each repository in the stats
        for repo_name, repo_stats in stats.items():
            if self.verbose:
                print(f'Processing repository: {repo_name}')

            # Create a directory for each repository
            repo_dir = os.path.join(plots_dir, repo_name)
            os.makedirs(repo_dir, exist_ok=True)

            # Generate plots for the repository
            self._generate_plots(repo_stats, repo_dir)

        return plots_dir

    def _generate_plots(self, stats, repo_dir):
        # Check if necessary data is available
        if 'build_times' not in stats or 'average_build_time' not in stats or 'success_rate' not in stats or 'performance_score' not in stats:
            print('Missing necessary data for plotting.')
            return

        # Create x-coordinates for the builds
        builds = list(range(len(stats['build_times'])))

        # Create and save the plot
        plt.figure(figsize=(10, 6))
        plt.plot(builds, stats['build_times'], 'b-', label='Build times')
        plt.plot(builds, [stats['average_build_time']] * len(builds), 'r-', label='Average build time')
        plt.title('Build times over consecutive builds')
        plt.xlabel('Build number')
        plt.ylabel('Seconds')
        plt.legend()

        # Add annotations for success rate and performance score
        plt.text(0.02, 0.95, f'Success Rate: {stats["success_rate"]}%', transform=plt.gca().transAxes)
        plt.text(0.02, 0.90, f'Performance Score: {stats["performance_score"]}', transform=plt.gca().transAxes)

        plt.tight_layout()
        plt.savefig(os.path.join(repo_dir, 'build_times.png'))
        plt.close()




