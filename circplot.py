#!/usr/bin/env python
# coding: utf-8

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

from sklearn.metrics import roc_curve, auc

import os 
import numpy as np
from matplotlib import pyplot as plt 
import pandas as pd 
import argparse

def plot_histogram(Df, is_weekend,grouping='hour'):
    # Filter the DataFrame based on whether it's the weekend or not
    Df['day_of_week'] = Df['datetime'].dt.dayofweek
    if is_weekend=='weekend':
        Df = Df[Df['day_of_week'].isin([5, 6])]  # 5 and 6 corresponds to Saturday and Sunday
    elif is_weekend=='weekday':
        Df = Df[~Df['day_of_week'].isin([5, 6])]

    # Group by the hour and the other column, and average the values
    hour_counts = Df.groupby(grouping)[f"tag_{args.tag}_bin"].mean().reset_index(name='counts')

    # Convert hours to radians
    if grouping=='hour':
        steps = 24
    elif grouping=='15_min_interval':
        steps = 24*4
    radians = np.linspace(0, 2*np.pi, steps)

    # Create the polar histogram
    plt.figure(figsize=(8,8))
    plt.subplot(111, polar=True)
    bars = plt.bar(radians, hour_counts['counts'], width=1.8*np.pi/steps, color='blue', alpha=0.7)

    # Set the direction of the zero hour
    plt.gca().set_theta_zero_location('S')
    plt.gca().set_theta_direction(-1)

    plt.gca().set_rmax(args.plot)  # Change this value to your desired maximum

   
    # Set the labels
    lines, labels = plt.thetagrids(range(0, 360, 15), (np.arange(24)), fmt='%d')

    if args.saveplot is not None:
        titleplot = args.input.split('/')[-1].split('.')[0] + '_' + is_weekend + '_' + args.tag
        plt.title(titleplot)
        plt.savefig(args.saveplot)
    else:
        plt.show()

def plot_histogram_both(Df):
    # Extract the day of the week
    Df['day_of_week'] = Df['datetime'].dt.dayofweek

    # Create a new column 'weekend' that is True if the time is between 3pm on Friday and midnight on Monday
    Df['weekend'] = ((Df['day_of_week'] == 4) & (Df['hour'] >= 15)) | (Df['day_of_week'] == 5) | (Df['day_of_week'] == 6)

    # Group by the hour and the other column, and sum the values for weekend and weekdays
    hour_counts_weekend = Df[Df['weekend']].groupby('hour')[f"tag_{args.tag}_bin"].mean().reset_index(name='counts')
    hour_counts_weekday = Df[~Df['weekend']].groupby('hour')[f"tag_{args.tag}_bin"].mean().reset_index(name='counts')

    # Convert hours to radians
    radians = np.linspace(0, 2*np.pi, 24)
    hours = np.arange(24)

    # Create the polar histogram
    plt.figure(figsize=(8,8))
    ax = plt.subplot(111, polar=True)

    # Adjust the width of the bars and plot the weekend and weekday data with different colors
    width = 1.8*np.pi/48  # Half the previous width
    bars_weekday = ax.bar(radians + width/2, hour_counts_weekday['counts'], width=width, color='red', alpha=0.7, label='Weekday')
    bars_weekend = ax.bar(radians - width/2, hour_counts_weekend['counts'], width=width, color='blue', alpha=0.7, label='Weekend')
    


    # Set the direction of the zero hour
    ax.set_theta_zero_location('S')
    ax.set_theta_direction(-1)

    # Set the maximum radial axis value
    ax.set_rmax(args.plot)  

    # Set the labels
    lines, labels = plt.thetagrids(range(0, 360, 15), (np.arange(24)), fmt='%d')

    # Add a legend
    ax.legend()
    if args.saveplot is not None:
        titleplot = args.input.split('/')[-1].split('.')[0] + '_' + args.tag
        plt.title(titleplot)
        plt.savefig(args.saveplot)
    else:
        plt.show()
    


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Circular plot of tagging')
    parser.add_argument('--input', default=None, type=str, help='Path to csv or pkl file')
    parser.add_argument('--tag', default=None, type=str, help='Name of category to threshold')
    parser.add_argument('--thr', default=None, type=float, help='Threshold value')
    parser.add_argument('--plot', default=None, type=float, help='Plot or not - if yes, max value for the plots')
    parser.add_argument('--circtype', default='dual', type=str, help='weekend vs week day or not')
    parser.add_argument('--grouping', default='hour', type=str, help='Grouping in hour or 15 min interval')
    parser.add_argument('--saveplot', default=None, type=str, help='Path to save plot')
    parser.add_argument('--savepath', default=None, type=str, help='Path to save output (thresholded, binary) csv')
    parser.add_argument('--saveagg', default=None, type=str, help='Path to save aggregate output')

    args = parser.parse_args()


    # Load data

    if args.input.endswith('.pkl'):
        from read_tagging import read_tagging_file
        Df = read_tagging_file(args.input)
    elif args.input.endswith('.csv'):
        Df = pd.read_csv(args.input)

    # Add datetime info 
    Df['datetime'] = pd.to_datetime(Df['datetime'], format='%Y%m%d_%H%M%S')
    Df['hour'] = Df['datetime'].dt.hour
    # Generate a grouping every 15 minutes
    Df['15_min_interval'] = Df['datetime'].dt.floor('15T').dt.time

    # Grab the column correspond to the tag
    col = Df[args.tag].copy()

    # Threshold and binarize
    if args.thr is not None:
        col[col < args.thr] = 0
        col[col >= args.thr] = 1
    
        Df[f"tag_{args.tag}_bin"] = col
    else:
        Df[f"tag_{args.tag}_bin"] = Df[args.tag]


    # Aggregate
        
    # Group by the hour and the other column, and average the values
    Df_agg = Df.groupby('15_min_interval')[["tag_bird","tag_insect","traffic","biophony","anthropophony","biophony"]].mean().reset_index()

    if args.saveagg is not None:
        sitename = args.input.split('/')[-1].split('.')[0]
        Df_agg.to_csv(os.path.join(args.saveagg, f"agg15min_{sitename}.csv"), index=False)

    # plot
    if args.plot is not None:        
        if args.circtype == 'dual':
            plot_histogram_both(Df)
        else:
            plot_histogram(Df, args.circtype,args.grouping)
        
        
    # Save
    if args.savepath is not None:
        Df.to_csv(os.path.join(args.savepath, f"thresholded_{args.tag}.csv"), index=False)
