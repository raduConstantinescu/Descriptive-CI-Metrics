import matplotlib.pyplot as plt
import numpy as np

def calculate_moving_average(churn_array, window_size):
    moving_averages = []

    for i in range(len(churn_array)):
        if i < window_size:
            window = churn_array[0:i + 1]
        else:
            window = churn_array[i - window_size + 1:i + 1]

        average = sum(window) / len(window)
        moving_averages.append(average)

    return moving_averages

def identify_implementation_periods(moving_average_values, average):
    implementation_periods = []

    for i in range(1, len(moving_average_values) - 1):
        current_value = moving_average_values[i]
        prev_value = moving_average_values[i - 1]
        next_value = moving_average_values[i + 1]

        if abs(current_value - prev_value) > average and abs(current_value - next_value) > average:
            print(current_value)
            implementation_periods.append(i)

    return implementation_periods


def see_weekly_code_chruns(code_frequency):
    # Example usage:
    weekly_churns = np.absolute(code_frequency)
    average = sum(weekly_churns) / len(weekly_churns)
    window_size = 26
    moving_averages = calculate_moving_average(weekly_churns, window_size)
    implementation_periods = identify_implementation_periods(moving_averages, average)

    week_number = 1  # Initial week number
    for period in implementation_periods:
        corresponding_week = week_number + period - window_size + 1

    # Calculate statistics
    average = np.mean(weekly_churns)
    median = np.median(weekly_churns)
    p25 = np.percentile(weekly_churns, 25)
    p75 = np.percentile(weekly_churns, 75)

    plt.show()
    # plt.subplot(1, 2, 1)
    # Create the line plot
    plt.plot(moving_averages, marker='o', linestyle='-', color='blue')
    plt.xlabel('Index')
    plt.ylabel('Value')
    plt.title('Weekly churns')

    # Add horizontal lines
    plt.axhline(average, color='red', linestyle='--', label='Average')
    plt.axhline(median, color='green', linestyle='--', label='Median')
    plt.axhline(p25, color='orange', linestyle='--', label='P25')
    plt.axhline(p75, color='purple', linestyle='--', label='P75')

    # Display the legend
    plt.legend()
    plt.show()