import pandas as pd
import numpy as np
import os

import seaborn as sns
import matplotlib.pyplot as plt

datapath = '/home/nfarrugi/Documents/datasets/EarthTalk/output/'

# list all csv files in datapath 
list_csv = [f for f in os.listdir(datapath) if f.endswith('.csv')]

# open them all and concatenate them in a single dataframe and a "site" column to identify them
list_df = []
for curcsv in list_csv:
    curdf = pd.read_csv(os.path.join(datapath,curcsv))    
    
    curdf['site'] = (curcsv.split('.')[0])
    list_df.append(curdf.sort_values(by=['datetime']))

df = pd.concat(list_df)
df.to_csv('tables/all_sites_tagging_agg.csv',index=False)