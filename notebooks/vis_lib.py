import matplotlib.pyplot as plt
import numpy as np 
import pandas as pd 


def vis_response_time_score_foreach(mydf, column):


    # Define log levels to visualize
    #log_levels = ["ERROR", "WARN", "INFO", "DEBUG"]
    log_levels = mydf[column].unique().tolist()

    # Determine the number of subplots needed
    num_levels = len(log_levels)
    
    # Calculate the number of rows and columns for subplots
    ncols = 2  # You can change this to your desired number of columns
    nrows = np.ceil(num_levels / ncols).astype(int)  # Calculate rows needed based on the number of log levels

    # Create subplots
    fig, axs = plt.subplots(nrows=nrows, ncols=ncols, figsize=(15, 5 * nrows))

    
    # Create subplots (2x2 grid for 4 log levels)
    #fig, axs = plt.subplots(2, 2, figsize=(15, 10))

    # Flatten the 2x2 grid of axes for easy iteration
    axs = axs.ravel()

    # Iterate through each log level and plot response_time and score for each one
    for i, log_level in enumerate(log_levels):
        # Filter data for the current log level
        data_subset = mydf[mydf[column] == log_level]

        # Create a twin axis for each subplot
        ax1 = axs[i]
        ax2 = ax1.twinx()

        # Plot response_time on the first y-axis
        ax1.plot(data_subset["response_time"], color="C0", alpha=0.8, label='Response Time')
        # Plot score on the second y-axis
        ax2.plot(data_subset["score"], color="C1", label='Anomaly Score')

        # Set axis labels
        ax1.set_ylabel("Response Time", color="C0")
        ax2.set_ylabel("Anomaly Score", color="C1")

        # Customize tick parameters
        ax1.tick_params("y", colors="C0")
        ax2.tick_params("y", colors="C1")

        # Set title for each subplot based on the log level
        ax1.set_title(f" {column}: {log_level}")

        # Optional: adjust y-axis limits if needed
        # ax1.set_ylim(0, max(data_subset["response_time"]))
        ax2.set_ylim(min(mydf["score"]), 1.4 * max(mydf["score"]))

    # Add a general title for the entire figure
    plt.suptitle("Response Time and Anomaly Score by Log Level", fontsize=16)

    # Adjust layout for better spacing
    plt.tight_layout(rect=[0, 0, 1, 0.95])

    # Show the plot
    plt.show()
