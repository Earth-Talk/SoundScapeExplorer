import streamlit as st
import numpy as np
import pandas as pd
from datetime import time
import gpxpy
import matplotlib.cm as cm
from matplotlib import pyplot as plt 

# Get the colormap
cmap = plt.colormaps['hot']
mycolors = {'traffic':'#770001','tag_bird':'#008E83','tag_insect':'#D17700'}

@st.cache_data
def get_data():

    gpx_file = open('/home/nfarrugi/Documents/datasets/ohm-pyr-2020/OHM_Vicdessos_20.21.gpx', 'r')

    gpx = gpxpy.parse(gpx_file)

    Df = pd.DataFrame()
    Df['site'] = [waypoint.name for waypoint in gpx.waypoints]
    Df['lat'] = [waypoint.latitude for waypoint in gpx.waypoints]
    Df['lon'] = [waypoint.longitude for waypoint in gpx.waypoints]
    gpx_file.close()

    Df_tag = pd.read_csv('all_sites_tagging_agg.csv')
    
    return Df, Df_tag

data_load_state = st.text('Loading data...')
Df,Df_tag = get_data()
data_load_state.text("Done! (using st.cache_data)")

Df_tag['15_min_interval'] = pd.to_datetime(Df_tag['15_min_interval'], format='%H:%M:%S').dt.time

selectime = st.slider(
    "Time:",
    value=(time(11, 30)))

ylimslider = st.slider(
    "Y axis limit:",0.0, 1.0,value=0.8)

Df_tag = Df_tag[Df_tag['15_min_interval'] == selectime]

Df_tag.drop(columns=['15_min_interval','biophony.1','biophony','anthropophony'], inplace=True)

# create a checkbox for each site
sitecheckboxes = [st.sidebar.checkbox(label) for label in Df_tag['site']]


# do a subdataframe with only the selected sites 
Df_tag_sub = Df_tag.loc[sitecheckboxes]



# bar plot of Df_tag_sub grouped by site
# Create a bar chart with Matplotlib
fig, ax = plt.subplots()

# Set the y-axis limits
ax.set_ylim([0, ylimslider])  # Replace with your desired limits

# Plot the data
Df_tag_sub.groupby('site').mean().plot(kind='bar', legend=False, ax=ax,color =[mycolors['tag_bird'],mycolors['tag_insect'],mycolors['traffic']] )

# add legend 
ax.legend()
# Display the plot in Streamlit
st.pyplot(fig)
if st.checkbox('Show raw data'):
    st.subheader('Raw data')
    st.write(Df_tag_sub)

#option = st.selectbox(
#    'Value to show', ['tag_bird','tag_insect','traffic'])

# Map the normalized values to colors
# Normalize your data to range between 0 and 1
#origvalues = Df_tag[option].to_numpy()
#normalized = (origvalues - origvalues.min()) / (origvalues.max() - origvalues.min())

#values = list(map(lambda x: cmap(x), normalized))

#Df_tag['orig'] = origvalues
#Df_tag['values'] = values

#Df = pd.merge(Df, Df_tag, on='site')
#Df = Df[['site','lat','lon',option]]
#Df = Df[['site','lat','lon','orig','values']]
#st.map(Df,color='values') """
