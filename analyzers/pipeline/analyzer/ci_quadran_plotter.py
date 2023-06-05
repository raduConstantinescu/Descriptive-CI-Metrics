import os
import matplotlib.pyplot as plt
import numpy as np
from ...utils import load_data
from analyzers.pipeline.stage import PipelineStage

class CIQuadrantPlotterConfig:
    def __init__(self, config):
        self.input_file = config["input_file"]
        self.stats_file = config["data_input_file"]
        self.output_dir = config["output_dir"]

class CIQuadrantPlotter(PipelineStage):
    def __init__(self, args, config):
        self.args = args
        self.config = config
        self.exclude_workflows = ['microsoft/playwright-tests-551665', 'ytdl-org/youtube-dl-CI-4378722']

    def run(self):
        data = load_data(self.config.input_file)
        overall_stats = load_data(self.config.stats_file)

        # Filter out excluded workflows
        data = {k: v for k, v in data.items() if k not in self.exclude_workflows}

        # Extract success rates and average execution times
        success_rates = [value['success_rate'] for value in data.values()]
        avg_execution_times = [value['average_execution_time'] / 60 for value in data.values()]  # convert to minutes

        # Create a new directory if it doesn't exist
        if not os.path.exists(self.config.output_dir):
            os.makedirs(self.config.output_dir)

        # Create the plot
        fig, ax = plt.subplots(figsize=(10,10))

        # Quadrant conditions
        conditions = [
            (np.array(success_rates) >= overall_stats['median_success_rate']) & (np.array(avg_execution_times) >= overall_stats['median_execution_time'] / 60),
            (np.array(success_rates) < overall_stats['median_success_rate']) & (np.array(avg_execution_times) >= overall_stats['median_execution_time'] / 60),
            (np.array(success_rates) >= overall_stats['median_success_rate']) & (np.array(avg_execution_times) < overall_stats['median_execution_time'] / 60),
            (np.array(success_rates) < overall_stats['median_success_rate']) & (np.array(avg_execution_times) < overall_stats['median_execution_time'] / 60)
        ]

        # Quadrant colors
        colors = ['red', 'green', 'blue', 'pink']

        for condition, color in zip(conditions, colors):
            ax.scatter(np.array(success_rates)[condition], np.array(avg_execution_times)[condition], color=color, s=10)

        # Draw median lines
        ax.axvline(x=overall_stats['median_success_rate'], color='red', linestyle='--', label=f'Median Success Rate: {overall_stats["median_success_rate"]:.2f}')
        ax.axhline(y=overall_stats['median_execution_time'] / 60, color='blue', linestyle='--', label=f'Median Execution Time: {overall_stats["median_execution_time"]/60:.2f} min')  # convert to minutes

        # Set labels and reverse x-axis
        ax.set_xlabel('Success Rate')
        ax.set_ylabel('Average Execution Time (min)')
        ax.set_xlim(1, 0)  # reverse x-axis

        # Calculate and display percentages and counts in the note
        counts = [np.count_nonzero(condition) for condition in conditions]
        total_count = len(data)
        percentages = [count / total_count * 100 for count in counts]
        note = f'Quadrant Percentages:\n'
        for i, percent in enumerate(percentages):
            note += f'Quadrant {i+1}: {percent:.2f}% ({counts[i]} workflows)\n'

        # Add the note to the plot
        ax.text(0.02, 0.98, note, verticalalignment='top', horizontalalignment='left', transform=ax.transAxes,
                bbox=dict(facecolor='white', edgecolor='gray', alpha=0.7))

        # Add titles to each quadrant in the background
        quadrant_titles = ['Quadrant 1', 'Quadrant 2', 'Quadrant 3', 'Quadrant 4']
        quadrant_x = [0.08, 0.08, 0.85, 0.85]
        quadrant_y = [0.78, 0.40, 0.78, 0.40]
        for title, x, y in zip(quadrant_titles, quadrant_x, quadrant_y):
            ax.text(x, y, title, fontsize=12, verticalalignment='center', horizontalalignment='center',
                    transform=ax.transAxes, backgroundcolor='white', alpha=0.7)

        # Add legend
        ax.legend(loc='upper right')

        # Save the plot
        plt.savefig(os.path.join(self.config.output_dir, 'quadrant_plot.png'))



