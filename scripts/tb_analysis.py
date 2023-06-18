import pandas as pd
from collections import defaultdict
import sys 
from datetime import datetime
from utils import get_exp_no, id_cols
import os

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


if __name__ == "__main__":
    participant_dir = sys.argv[1] #PT or HC - i.e. Patient or Healthy Control directories
    search_dir = '../data/cleaned_data/'+participant_dir+'/'

    # reading in our relevant data files (task variables, questionnaire scores, demographics info) as pandas dataframes
    ft_df = get_latest_file_as_df("FT_INFO", search_dir)
    demo_df = get_latest_file_as_df("DEMO", search_dir)
    q_df = get_latest_file_as_df("Q_scored", search_dir)

