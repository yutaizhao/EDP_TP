import os
import json
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from decimal import Decimal

# Function to read JSON files and extract relevant parameters
def extract_bandwidth(file_pattern, output_dir, variable=None):
    data = []

    # Iterate over all files in the output directory
    for file in os.listdir(output_dir):
        if file.startswith(file_pattern) and file.endswith('_output.json'):
            file_path = os.path.join(output_dir, file)
            with open(file_path, 'r') as f:
                result = json.load(f)
                job = result['jobs'][0]
                write_bw = job['write']['bw']  # Extract write bandwidth in KB/s
                read_bw = job['read']['bw']    # Extract read bandwidth in KB/s

                if variable:
                    # Extract the varying parameter from filename based on the experiment type
                    if variable == 'write_percentage':
                        var_value = float(file.split('_')[2])
                    elif variable == 'blocksize':
                        var_value = file.split('_')[2]
                    elif variable == 'numjobs':
                        var_value = int(file.split('_')[2])
                    data.append({variable: var_value, 'write_bandwidth': write_bw, 'read_bandwidth': read_bw})
                else:
                    # For bssplit where there is no varying parameter
                    latency_percentiles = job['write']['clat_ns']['percentile']
                    
                    # Define the desired percentiles
                    desired_percentiles = [
                        '10.000000', '20.000000', '30.000000',
                        '40.000000', '50.000000', '60.000000', '70.000000',
                        '80.000000', '90.000000', '99.990000'
                    ]

                    # Filter the latency_percentiles to keep only the desired percentiles
                    latency_percentiles = {
                        k: v for k, v in latency_percentiles.items() if k in desired_percentiles
                    }

                    latency_percentiles = {Decimal(k): v for k, v in latency_percentiles.items()}
                    data.append({'write_bandwidth': write_bw, 'read_bandwidth': read_bw, 'latency_percentiles': latency_percentiles})

    return pd.DataFrame(data)

# List of datasets to process with corresponding variable names (None for bssplit)
datasets = {
    "Ex1 seq": ("Exo1_seq", "./fio_results_Exo1", "write_percentage"),
    "Ex1 rand": ("Exo1_rand", "./fio_results_Exo1", "write_percentage"),
    "Ex2 bs": ("Exo2_bs", "./fio_results_Exo2", "blocksize"),
    "Ex3 bssplit": ("Exo3_bssplit", "./fio_results_Exo3", None),  # No varying parameter for bssplit
    "Ex4 parallel": ("Exo4_parallel", "./fio_results_Exo4", "numjobs")
}

# Extract data for all tasks and calculate stats
data_stats = {}

for key, (file_pattern, output_dir, variable) in datasets.items():
    # Extract data
    data = extract_bandwidth(file_pattern, output_dir, variable)
    
    # For datasets with a varying parameter, calculate stats for write, read, and total bandwidth
    if variable:
        # Calculate write and read stats
        write_stats = data.groupby(variable)['write_bandwidth'].agg(['mean', 'std', 'median']).reset_index()
        read_stats = data.groupby(variable)['read_bandwidth'].agg(['mean', 'std', 'median']).reset_index()
        
        # Calculate total bandwidth
        data['total_bandwidth'] = data['write_bandwidth'] + data['read_bandwidth']
        total_stats = data.groupby(variable)['total_bandwidth'].agg(['mean', 'std', 'median']).reset_index()

        # For bs dataset, sort by the specified block size order
        if key == "Ex2 bs":
            order = ['1k', '2k', '4k', '8k', '16k', '32k', '64k', '128k', '256k', '512k', '1m']
            write_stats['blocksize'] = pd.Categorical(write_stats[variable], categories=order, ordered=True)
            read_stats['blocksize'] = pd.Categorical(read_stats[variable], categories=order, ordered=True)
            total_stats['blocksize'] = pd.Categorical(total_stats[variable], categories=order, ordered=True)
            # Sort stats by the specified order
            write_stats = write_stats.sort_values('blocksize')
            read_stats = read_stats.sort_values('blocksize')
            total_stats = total_stats.sort_values('blocksize')
        
        # Store stats in a dictionary
        data_stats[key] = {
            'write': write_stats,
            'read': read_stats,
            'total': total_stats,
            'variable': variable
        }
    else:
        # For bssplit, calculate the mean, std, and median for write, read, and total bandwidth directly
        write_stats = data['write_bandwidth'].agg(['mean', 'std', 'median']).to_frame().transpose().reset_index(drop=True)
        read_stats = data['read_bandwidth'].agg(['mean', 'std', 'median']).to_frame().transpose().reset_index(drop=True)
        
        # Calculate total bandwidth
        data['total_bandwidth'] = data['write_bandwidth'] + data['read_bandwidth']
        total_stats = data['total_bandwidth'].agg(['mean', 'std', 'median']).to_frame().transpose().reset_index(drop=True)
        
        # Calculate latency percentiles
        latency_data = pd.DataFrame(list(data['latency_percentiles']))
        latency_stats = latency_data.apply(lambda x: x.agg(['mean', 'std', 'median']))

        # Store stats in a dictionary
        data_stats[key] = {
            'write': write_stats,
            'read': read_stats,
            'total': total_stats,
            'latency': latency_stats
        }

# Plotting the bar plots for read and write side by side
def plot_read_write_bandwidth(write_stats, read_stats, variable, filename):
    if variable:
        x_labels = write_stats[variable]
        write_means = write_stats['mean']
        write_stds = write_stats['std']
        write_medians = write_stats['median']
        read_means = read_stats['mean']
        read_stds = read_stats['std']
        read_medians = read_stats['median']

        x = np.arange(len(x_labels))
        width = 0.35

        fig, ax = plt.subplots(figsize=(12, 7))
        bars1 = ax.bar(x - width/2, write_means, width, yerr=write_stds, capsize=5, label='Write Bandwidth', alpha=0.6, color='b')
        bars2 = ax.bar(x + width/2, read_means, width, yerr=read_stds, capsize=5, label='Read Bandwidth', alpha=0.6, color='g')

        # Plot median as scatter points
        ax.scatter(x - width/2, write_medians, color='r', label='Write Median', zorder=3)
        ax.scatter(x + width/2, read_medians, color='orange', label='Read Median', zorder=3)

        # Labels and title
        ax.set_xlabel(f'{variable.replace("_", " ").capitalize()}')
        ax.set_ylabel('Bandwidth (KB/s)')
        ax.set_xticks(x)
        ax.set_xticklabels(x_labels)
        ax.legend()

    else:
        # For bssplit, there are no varying parameters, so plot a single bar for write and read
        fig, ax = plt.subplots(figsize=(6, 6))
        bars1 = ax.bar(['Write Bandwidth'], write_stats['mean'], yerr=write_stats['std'], capsize=5, alpha=0.6, color='b')
        bars2 = ax.bar(['Read Bandwidth'], read_stats['mean'], yerr=read_stats['std'], capsize=5, alpha=0.6, color='g')

        # Plot median as scatter points
        ax.scatter(['Write Bandwidth'], write_stats['median'], color='r', label='Write Median', zorder=3)
        ax.scatter(['Read Bandwidth'], read_stats['median'], color='orange', label='Read Median', zorder=3)

        # Labels and title
        ax.set_ylabel('Bandwidth (KB/s)')
        ax.legend()

    # Set y-axis max
    if variable == "write_percentage" :
        plt.ylim(top=3*10**5)
    elif variable == "blocksize" :
        plt.ylim(top=1.2*10**6)
    elif variable == None :
        plt.ylim(top=2*10**5)
    elif variable == "numjobs" :
        plt.ylim(top=2*10**5)
    
    # Set y-axis ticks with an increment of 10^5
    # ax.yaxis.set_major_locator(plt.MultipleLocator(10**5))

    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.tight_layout()

    # Save the plot to the current directory
    plt.savefig(filename)
    plt.close()  # Close the figure to free memory

# Plotting total bandwidth bar plot
def plot_total_bandwidth(stats, variable, filename):
    if variable:
        x_labels = stats[variable]
        means = stats['mean']
        stds = stats['std']
        medians = stats['median']

        x = np.arange(len(x_labels))
        width = 0.35

        fig, ax = plt.subplots(figsize=(10, 6))
        bars = ax.bar(x, means, width, yerr=stds, capsize=5, label='Total Bandwidth', alpha=0.6, color='purple')

        # Plot median as scatter points
        ax.scatter(x, medians, color='r', label='Median Bandwidth', zorder=3)

        # Labels and title
        ax.set_xlabel(f'{variable.replace("_", " ").capitalize()}')
        ax.set_ylabel('Bandwidth (KB/s)')
        ax.set_xticks(x)
        ax.set_xticklabels(x_labels)
        ax.legend()

    else:
        # For bssplit, there is no varying parameter, so plot a single bar for total bandwidth
        fig, ax = plt.subplots(figsize=(6, 6))
        bars = ax.bar(['Total Bandwidth'], stats['mean'], yerr=stats['std'], capsize=5, alpha=0.6, color='purple')

        # Plot median as scatter points
        ax.scatter(['Total Bandwidth'], stats['median'], color='r', label='Median Bandwidth', zorder=3)

        # Labels and title
        ax.set_ylabel('Bandwidth (KB/s)')
        ax.legend()
    
    # Set y-axis max
    if variable == "write_percentage" :
        plt.ylim(top=3*10**5)
    elif variable == "blocksize" :
        plt.ylim(top=1.2*10**6)
    elif variable == None :
        plt.ylim(top=2*10**5)
    elif variable == "numjobs" :
        plt.ylim(top=2*10**5)

    # Set y-axis ticks with an increment of 10^5
    # ax.yaxis.set_major_locator(plt.MultipleLocator(10**5))

    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.tight_layout()

    # Save the plot to the current directory
    plt.savefig(filename)
    plt.close()  # Close the figure to free memory

# Plotting deciles of latency for Exo3
def plot_latency_deciles(latency_stats, filename):
    percentiles = latency_stats.columns
    means = latency_stats.loc['mean']
    stds = latency_stats.loc['std']
    medians = latency_stats.loc['median']

    x = np.arange(len(percentiles))
    width = 0.5

    fig, ax = plt.subplots(figsize=(10, 6))
    bars = ax.bar(x, means, width, yerr=stds, capsize=5, label='Mean Latency', color='b', alpha=0.6)

    # Plot median as scatter points
    ax.scatter(x, medians, color='r', label='Median Latency', zorder=3)

    # Labels and title
    ax.set_xlabel('Centiles (%)')
    ax.set_ylabel('Latency (ns)')
    ax.set_xticks(x)
    ax.set_xticklabels([float(p) for p in percentiles])  # Convert percentile labels to integer without trailing zeros
    ax.legend()

    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.tight_layout()

    # Save the plot to the current directory
    plt.savefig(filename)
    plt.close()  # Close the figure to free memory

# Plot read and write bandwidth, total bandwidth, and latency deciles for all datasets
for key in datasets.keys():
    # Extract the corresponding variable for labeling
    variable = data_stats[key].get('variable', None)

    # Read and write bandwidth plot
    write_stats = data_stats[key]['write']
    read_stats = data_stats[key]['read']
    plot_read_write_bandwidth(write_stats, read_stats, variable,
                              f'{key}_read_write_bandwidth_plot.png')
    
    # Total bandwidth plot
    total_stats = data_stats[key]['total']
    plot_total_bandwidth(total_stats, variable,
                         f'{key}_total_bandwidth_plot.png')

    # Latency deciles plot for Exo3
    if key == "Ex3 bssplit":
        latency_stats = data_stats[key]['latency']
        plot_latency_deciles(latency_stats, f'{key}_latency_deciles_plot.png')

