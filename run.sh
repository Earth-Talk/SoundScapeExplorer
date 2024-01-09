#!/bin/bash
# Define the tag
tag="traffic"

# Define the directory to scan for .pkl files
dir="/home/nfarrugi/Documents/datasets/ohm-pyr-2020/"

# Loop over all .pkl files in the specified directory
for file in "$dir"/tagging_site_*.pkl
do
    # Generate the saveplot name
    saveplot_name="${file%.pkl}_${tag}_0.25_plot.svg"

    # Run threshold.py with the current file as the input and the generated name as the saveplot
    python circplot.py --input "$file" --tag "$tag" --plot 0.25 --saveplot "$saveplot_name" --circtype all --grouping 15_min_interval
done


# Define the tag
tag="tag_bird"

# Define the directory to scan for .pkl files
dir="/home/nfarrugi/Documents/datasets/ohm-pyr-2020/"

# Loop over all .pkl files in the specified directory
for file in "$dir"/tagging_site_*.pkl
do
    # Generate the saveplot name
    saveplot_name="${file%.pkl}_${tag}_0.4_plot.svg"

    # Run threshold.py with the current file as the input and the generated name as the saveplot
    python circplot.py --input "$file" --tag "$tag" --plot 0.4 --saveplot "$saveplot_name" --circtype all --grouping 15_min_interval
done

# Define the tag
tag="tag_insect"

# Define the directory to scan for .pkl files
dir="/home/nfarrugi/Documents/datasets/ohm-pyr-2020/"

# Loop over all .pkl files in the specified directory
for file in "$dir"/tagging_site_*.pkl
do
    # Generate the saveplot name
    saveplot_name="${file%.pkl}_${tag}_0.7_plot.svg"

    # Run threshold.py with the current file as the input and the generated name as the saveplot
    python circplot.py --input "$file" --tag "$tag" --plot 0.7 --saveplot "$saveplot_name" --circtype all --grouping 15_min_interval
done