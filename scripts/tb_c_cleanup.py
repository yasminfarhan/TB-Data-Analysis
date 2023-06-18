import pandas as pd
import sys
from datetime import datetime
from utils import get_exp_no, gen_cleaned_task_data

# function to reformat single idx string (from Public ID), starting from correctly formatted start string
def format_index(id):
    start_index = id.find('8247')
    return id[start_index:].strip()
    
def parse_task_df(df):
    task_cols = ['Participant Public ID', 'Participant Private ID', 'Task Name', 'Experiment Version', 'Trial Number', 'Reaction Time', 'Correct']

    # filter out unnecessary rows & select specific columns
    participant_data = df.loc[(df['Screen Name'] == 'test_sample') & (df['display'] == 'trial'), task_cols]

    # select specific columns
    participant_data.set_index('Participant Public ID', inplace=True)

    # Reformat the index values using the custom function - assuming at least one is incorrectly formatted
    participant_data = participant_data.rename(index=lambda x: format_index(x))

    return participant_data.sort_index()

def main():
    participant_dir = sys.argv[1] #PT or HC - i.e. Patient or Healthy Control directories
    exp_no = get_exp_no("C", participant_dir) #experiment number in Gorilla - used for naming the output files

    current_date = datetime.now().strftime("%Y_%m_%d") #for keeping track of when data files were generated
    suffix = "data_exp_"+exp_no+'-'+current_date
    save_dir = '../data/cleaned_data/'+participant_dir+'/'
    path_to_task_dir = '../data/raw_data/'+participant_dir+'/'

    task_df = gen_cleaned_task_data(parse_task_df, path_to_task_dir, "C - Delay Match to Sample")

    # writing C relevant dataframes to csv files
    task_df.to_csv(save_dir+'C-task_info-'+suffix+'.csv', index=True)
main()