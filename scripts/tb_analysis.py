import pandas as pd
from collections import defaultdict
import sys 
from datetime import datetime
from utils import get_exp_no, id_cols
import os
from scipy import stats
import numpy as np

# function to get the most recently dated file with a specific search string
def get_latest_file_as_df(search_string, search_directory):
    matching_files = []

    # Iterate over files in the search directory
    for root, dirs, files in os.walk(search_directory):
        for file in files:
            # Check if the file name contains the search string
            if search_string in file:
                file_path = os.path.join(root, file)
                matching_files.append(file_path)

    if matching_files:
        # Sort matching files by modification time (most recent first)
        matching_files.sort(key=lambda x: os.path.getmtime(x), reverse=True)
    
        # read the filename into a pandas dataframe, assume index col is first col
        df = pd.read_csv(matching_files[0], index_col=0)

        return df
    else:
        return None

# we don't want to exclude any patients for now
def exclude_pp(df):
    df_excl = df.copy()

    # drop any NaN values from the dataframe
    df_excl = df_excl.dropna()

    # excluding participants that chose the 'Find out now' option exactly 12 or 13 times out of 25 trials
    # implying that they chose the same button (lefthand side or righthand side) for the entire experiment 
    # since the position of the 'find out now' option is counterbalanced throughout the experiment
    df_excl = df_excl.loc[(df_excl['B_PROP_FON'] != 0.48) & (df_excl['B_PROP_FON'] != 0.52)]

    # specify the columns for which we want to exclude outliers
    exclude_cols = ['AV1_ART', 'AV1_ACC', 'AV3_ART', 'AV3_ACC', 'B_ART', 'C_ART', 'C_ACC', 'D1_NUM_TIMEOUTS', 'D1_1B_TGT_ACC', 'D1_2B_TGT_ACC', 'D1_3B_TGT_ACC', 'D1_4B_TGT_ACC', 'D1_5B_TGT_ACC', 'D1_6B_TGT_ACC', 'D1_1B_NON_TGT_ACC', 'D1_2B_NON_TGT_ACC', 'D1_3B_NON_TGT_ACC', 'D1_4B_NON_TGT_ACC', 'D1_5B_NON_TGT_ACC', 'D1_6B_NON_TGT_ACC', 'D3_NUM_TIMEOUTS']

    # define the condition for exclusion
    exclude_condition = (np.abs(stats.zscore(df_excl[exclude_cols]) > 3)).any(axis=1)

    # exclude rows based on the condition
    df_excl = df_excl.loc[~exclude_condition]

    return df_excl

if __name__ == "__main__":
    participant_dir = sys.argv[1] #PT or HC - i.e. Patient or Healthy Control directories
    search_dir = '../data/cleaned_data/'+participant_dir+'/'

    # reading in our relevant data files (task variables, questionnaire scores, demographics info) as pandas dataframes
    ft_df = get_latest_file_as_df("FT_INFO", search_dir)
    demo_df = get_latest_file_as_df("DEMO", search_dir)
    q_df = get_latest_file_as_df("Q_scored", search_dir)