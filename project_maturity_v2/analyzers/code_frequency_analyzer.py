import ast
import numpy as np

from project_maturity_v2.utils import extract_data_from_json


class CodeFrequencyAnalyzer():
    def __init__(self):
        self.data = extract_data_from_json('outputs_v2/repo_data.json')

    def analyze(self, repo_name):
        if repo_name not in self.data.keys():
            return False

        repo_data = self.data[repo_name]
        weekly_code_frequencies = np.absolute(ast.literal_eval(repo_data["weekly_code_frequency"]))
        code_frequency_intervals = self.create_code_frequency_intervals(weekly_code_frequencies)
        has_constant_code_frequency = self.analyze_code_frequency(weekly_code_frequencies, code_frequency_intervals)
        last_year_activity = self.analyze_activity(weekly_code_frequencies)
        if has_constant_code_frequency and last_year_activity:
            return True
        return False

    def create_code_frequency_intervals(self, code_frequencies):
        interval_length = 26
        intervals = []
        # Group code frequencies into intervals
        for i in range(0, len(code_frequencies), interval_length):
            interval_frequencies = code_frequencies[i:i + interval_length]
            intervals.append(interval_frequencies)

        return intervals

    def analyze_code_frequency(self, code_frequencies, intervals):
        dynamic_threshold_ratio = 0.8 # Adjust this ratio based on your requirements
        total_lines_changed = sum(code_frequencies)
        average_frequency = np.median(code_frequencies)
        dynamic_threshold = dynamic_threshold_ratio * average_frequency
        interval_count = 0
        # Check for intervals with a constant stream of commits
        for i, frequencies in enumerate(intervals):
            above_threshold_count = sum(1 for freq in frequencies if freq >= dynamic_threshold)
            above_threshold_percentage = above_threshold_count / len(frequencies)

            constant_stream = above_threshold_percentage >= 0.8 and 0 not in frequencies

            if constant_stream and i != len(intervals)-1:
                interval_count +=1
            if interval_count == 2:
                break
        if interval_count ==2:
            return True

        return False

    def analyze_activity(self, code_frequencies):
        last_year_frequencies = code_frequencies[len(code_frequencies)-1-56:len(code_frequencies)-1]
        count_activity_weeks = sum(1 for freq in last_year_frequencies if freq >= 0)
        if count_activity_weeks >= 14:
            return True
        return False
