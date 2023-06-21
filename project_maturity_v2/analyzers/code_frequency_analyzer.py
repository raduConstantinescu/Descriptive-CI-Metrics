import ast

from project_maturity_v2.utils import extract_data_from_json


class CodeFrequencyAnalyzer():
    def __init__(self):
        self.data = extract_data_from_json('../outputs_v2/repo_data.json')

    def analyze(self, repo_name):
        if repo_name not in self.data.keys():
            return False

        repo_data = self.data[repo_name]
        weekly_code_frequencies = ast.literal_eval(repo_data["weekly_code_frequency"])
        code_frequency_intervals = self.create_code_frequency_intervals(weekly_code_frequencies)
        return self.analyze_code_frequency(weekly_code_frequencies, code_frequency_intervals)

    def create_code_frequency_intervals(self, code_frequencies):
        interval_length = 26
        intervals = []
        # Group code frequencies into intervals
        for i in range(0, len(code_frequencies), interval_length):
            interval_frequencies = code_frequencies[i:i + interval_length]
            intervals.append(interval_frequencies)

        return intervals

    def analyze_code_frequency(self, code_frequencies, intervals):
        dynamic_threshold_ratio = 0.3 # Adjust this ratio based on your requirements
        total_lines_changed = sum(code_frequencies)
        average_frequency = total_lines_changed / len(code_frequencies)
        dynamic_threshold = dynamic_threshold_ratio * average_frequency
        # Check for intervals with a constant stream of commits
        for i, frequencies in enumerate(intervals):
            above_threshold_count = sum(1 for freq in frequencies if freq >= dynamic_threshold)
            above_threshold_percentage = above_threshold_count / len(frequencies)

            constant_stream = above_threshold_percentage >= 0.8 and 0 not in frequencies

            if constant_stream:
                return True
        return False

