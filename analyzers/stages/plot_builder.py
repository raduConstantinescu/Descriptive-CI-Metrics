import matplotlib.pyplot as plt
import json
import os

from analyzers.stages.stage import PipelineStage

class PlotBuilder(PipelineStage):
    def __init__(self, verbose=True):
        self.verbose = verbose

    def run(self, input):
        with open(os.path.join('output', 'build_stats.json'), 'r') as f:
            data = json.load(f)

        for repo_name, stats in data.items():
            if self.verbose:
                print(f'Plotting repository: {repo_name}')
            fig, ax = plt.subplots(2, 2, figsize=(10, 10))

            # Performance Score
            ax[0, 0].plot(stats['performance_score'], color='blue')
            ax[0, 0].set_title('Performance Score')

            # Flakeiness
            ax[0, 1].plot(stats['build_flakiness'], color='purple')
            ax[0, 1].set_title('Build Flakeiness')

            # Average Build Time
            ax[1, 0].plot(stats['average_build_time'], color='orange')
            ax[1, 0].set_title('Average Build Time')

            # Success Rate
            ax[1, 1].plot(stats['success_rate'], color='green')
            ax[1, 1].set_title('Success Rate')

            # Adjust for the repository
            fig.suptitle(f'Stats for {repo_name}', fontsize=16)

            plt.savefig(os.path.join('output', f'{repo_name}_stats.png'))

        return None
