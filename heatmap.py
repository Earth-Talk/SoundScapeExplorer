import pandas as pd
import numpy as np
import os

import seaborn as sns
import matplotlib.pyplot as plt


datapath = '/home/nfarrugi/Documents/datasets/ohm-pyr-2020/'

# list all csv files in datapath 
list_csv = [f for f in os.listdir(datapath) if f.endswith('.csv')]
# keep only the ones that begin with 'site_'
list_csv = [f for f in list_csv if f.startswith('site_')]

# open them all and concatenate them in a single dataframe and a "site" column to identify them
list_df = []
for curcsv in list_csv:
    curdf = pd.read_csv(os.path.join(datapath,curcsv))
    # keep only the name and datetime columns
    curdf = curdf[['name','datetime']]
    # remove duplicate lines according to the name column
    curdf = curdf.drop_duplicates(subset='name')
    curdf['site'] = curcsv.split('.')[0]
    list_df.append(curdf.sort_values(by=['datetime']))

df = pd.concat(list_df)
df.to_csv('all_sites_files.csv',index=False)

df['datetime'] = pd.to_datetime(df['datetime'], format='%Y%m%d_%H%M%S')

# Extract date from datetime
df['date'] = df['datetime'].dt.date

# Group by 'site' and 'date' and count the number of rows for each group
grouped = df.groupby(['site', 'date']).size().reset_index(name='counts')

# Pivot the data
pivot = grouped.pivot('site', 'date', 'counts')

# Create the heatmap
plt.figure(figsize=(10, 8))
sns.heatmap(pivot, cmap='viridis',yticklabels=1)

plt.title('Number of recordings for each site')
# Rotate y-axis labels
#plt.yticks(rotation=45)
plt.tight_layout()
plt.savefig('heatmap.pdf')
plt.show()