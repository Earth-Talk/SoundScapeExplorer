import streamlit as st
import numpy as np
import pandas as pd
from datetime import time, timedelta
import matplotlib.cm as cm
from matplotlib import pyplot as plt 
import os
from librosa import load
import noisereduce as nr

datapath = '/home/nfarrugi/Documents/datasets/EarthTalk/output/'

## list all directories in the path


@st.cache_data
def get_data():
    Df_tag = pd.read_csv('tables/all_sites_tagging_agg.csv')
    
    return Df_tag

def mix_flac_files(Df_tag_sub, num_sounds,crossfade = 0.5, fadelen = 0.05):
    
    # get the list of flac files
    flac_files = Df_tag_sub['flac_path'].tolist()
    # permute the list
    #flac_files = np.random.shuffle(flac_files)
    # get the number of sounds to mix
    num_sounds = min(num_sounds, len(flac_files))

    ## reorganise the list as a 2D array with num_sounds rows and as many columns as needed
    # reshape the list
    num_files = len(flac_files)
    nrows = int(np.floor(num_files / num_sounds))
    # drop the last row if it is not full
    flac_files = flac_files[:nrows*num_sounds]

    flac_files = np.array(flac_files).reshape(nrows, num_sounds)

    mixed_audio = []
    for currow in range(nrows):
        # get the list of flac files for this row
        flac_files_row = flac_files[currow]
        # create a list to store the audio data
        audio_data = []
        
        for flac_file in flac_files_row:
            # read the audio file
            X_audio, sr = load(flac_file, sr=None)
            if denoise:
                X_audio = nr.reduce_noise(y=X_audio, sr=sr)
            audio_data.append(X_audio)
        
        audio_data = np.array(audio_data)
        mix = np.mean(audio_data,0)
        if denoiseglobal:
            mix = nr.reduce_noise(y=mix, sr=sr,stationary=True)
        # mix the audio data
        mixed_audio.append(mix)
        fadelength = int(sr * fadelen)
        ## apply a fade in and fade out to the mixed audio
        fade_in = np.linspace(0, 1, fadelength)
        fade_out = np.linspace(1, 0, fadelength)
        mixed_audio[currow][:fadelength] *= fade_in
        mixed_audio[currow][-fadelength:] *= fade_out

    mixed_audio = np.array(mixed_audio)
    # concatenate the mixed audio with a crossfade between the rows (cross fade in seconds in the variable named crossfade)
    
    mixed_audio = np.concatenate(mixed_audio)
    # for currow in range(1, nrows):
    #     # get the length of the crossfade
    #     crossfade_length = int(sr * crossfade)
    #     # get the start and end of the crossfade
    #     start = (currow - 1) * num_sounds + num_sounds - crossfade_length
    #     end = currow * num_sounds
    #     # apply the crossfade
    #     mixed_audio[start:end] *= np.linspace(1, 0, crossfade_length)
    
    
    return mixed_audio

data_load_state = st.text('Loading data...')
Df_tag = get_data()
data_load_state.text("Done! (using st.cache_data)")

selectime = st.slider(
    "Time:",
    value=(time(11, 30), time(13, 30)),
    step=timedelta(minutes=5)  # 5-minute intervals
)

taglist = ['biophony', 'anthropophony', 'geophony','buzz','tag_Car','tag_Bird']
tagselect = {}
for curtag in taglist:
    tagselect[curtag] = st.slider(label=f"{curtag}", min_value=0., max_value=1., value=(0.,1.), step=0.05)

# sort Df_tag by site
Df_tag.sort_values(by=['site'], inplace=True)
# create a checkbox for each site
st.sidebar.subheader('Select sites to plot')
# get the unique sites
sites = Df_tag['site'].unique()
# create a checkbox for each site
sitecheckboxes = [st.sidebar.checkbox(label) for label in sites]

## An integer to select how many sounds to mix, as an text input
num_sounds = st.sidebar.number_input("Number of sounds to mix", min_value=1, max_value=1000, value=1, step=1)

## checkbox for denoising
denoise = st.sidebar.checkbox("Denoise", value=True)
denoiseglobal = st.sidebar.checkbox("Denoising Global", value=True)


### beginning of filtering

# do a subdataframe with only the selected sites 
Df_tag_sub = Df_tag[Df_tag['site'].isin(sites[sitecheckboxes])]

## filter the data by time
## current format is 20241024_170401 YYYYMMDD_HHMMSS

# convert the time column to datetime
Df_tag_sub['time'] = pd.to_datetime(Df_tag_sub['datetime'], format='%Y%m%d_%H%M%S').dt.time

# filter the data by time
Df_tag_sub = Df_tag_sub[(Df_tag_sub['time'] >= selectime[0]) & (Df_tag_sub['time'] <= selectime[1])]

# filter the data by tags
for curtag in taglist:
    # filter the data by tags
    Df_tag_sub = Df_tag_sub[(Df_tag_sub[curtag] >= tagselect[curtag][0]) & (Df_tag_sub[curtag] <= tagselect[curtag][1])]

# change "indices" to "audio" in the strings of the column "site" and create a new column "audio"
Df_tag_sub['audio'] = Df_tag_sub['site'].str.replace('indices', 'audio')

# if no site is selected, print a message
if Df_tag_sub.empty:
    st.write("No data left")
else:

    ## recreate the absolute path and names of the flac files 
    Df_tag_sub['flac_path'] = datapath + Df_tag_sub['audio'] + '/' + Df_tag_sub['datetime'] + '.flac'


    st.write(f"Selected {len(Df_tag_sub)} data points from {len(sites[sitecheckboxes])} sites")

    st.subheader('Raw data')
    st.write(Df_tag_sub)

    ## add a button that when pressed, will mix the sounds and play them
    if st.button('Mix sounds'):
        ## Shuffle the rows of the dataframe
        Df_tag_sub = Df_tag_sub.sample(frac=1).reset_index(drop=True)
    
        # mix the sounds
        mixed_audio = mix_flac_files(Df_tag_sub, num_sounds)
        # play the sounds
        st.audio(mixed_audio, format='audio/wav',sample_rate=48000)
        st.write("Sounds mixed and played")
    else:
        st.write("Press the button to mix the sounds")


