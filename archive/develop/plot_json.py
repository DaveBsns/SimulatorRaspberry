import json
import matplotlib.pyplot as plt
import numpy as np

def load_and_plot():
    # Load the JSON data
    with open('rizer_data.json', 'r') as f:
        data = json.load(f)

    # Extract the first element from each inner list for all four categories
    single_y_values_1 = [inner_list[0] for inner_list in data]
    single_y_values_2 = [inner_list[1] for inner_list in data]
    single_y_values_3 = [inner_list[2] for inner_list in data]
    single_y_values_4 = [inner_list[3] for inner_list in data]

    # Create a 2x2 grid of subplots
    fig, axs = plt.subplots(2, 2, figsize=(15, 12))

    # Plot Category 1
    axs[0, 0].plot(range(len(data)), single_y_values_1, color='blue', label='First Value')
    axs[0, 0].set_title('Category 1')
    axs[0, 0].set_xlabel('Index')
    axs[0, 0].set_ylabel('Value')
    axs[0, 0].legend()

    # Plot Category 2
    axs[0, 1].plot(range(len(data)), single_y_values_2, color='green', label='Second Value')
    axs[0, 1].set_title('Category 2')
    axs[0, 1].set_xlabel('Index')
    axs[0, 1].set_ylabel('Value')
    axs[0, 1].legend()

    # Plot Category 3
    axs[1, 0].plot(range(len(data)), single_y_values_3, color='red', label='Third Value')
    axs[1, 0].plot(range(len(data)), single_y_values_4, color='purple', label='Fourth Value')
    axs[1, 0].set_title('Category 3')
    axs[1, 0].set_xlabel('Index')
    axs[1, 0].set_ylabel('Value')
    axs[1, 0].legend()

    # Plot Category 4
    axs[1, 1].plot(range(len(data)), single_y_values_4, color='purple', label='Fourth Value')
    axs[1, 1].set_title('Category 4')
    axs[1, 1].set_xlabel('Index')
    axs[1, 1].set_ylabel('Value')
    axs[1, 1].legend()

    # Adjust layout
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    load_and_plot()
