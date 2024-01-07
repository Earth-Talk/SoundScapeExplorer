#!/bin/bash

# Define the tag
tag="tag_insect"

# Define the directory to scan for .pkl files
dir="/home/nfarrugi/Documents/datasets/ohm-pyr-2020/"

# Loop over all .pkl files in the specified directory
for file in "$dir"/tagging_site_*.pkl
do
    # Generate the saveplot name
    saveplot_name="${file%.pkl}_${tag}_plot.png"

    # Run threshold.py with the current file as the input and the generated name as the saveplot
    python circplot.py --input "$file" --tag "$tag" --plot 0.6 --saveplot "$saveplot_name" --circtype all
done