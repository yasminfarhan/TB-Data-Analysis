import pandas as pd
import sys
from datetime import datetime
from utils import get_exp_no, gen_cleaned_task_data, id_cols

participant_dir = sys.argv[1] #PT or HC - i.e. Patient or Healthy Control directories

# function to reformat single idx string (from Public ID), starting from correctly formatted start string
def format_index(id):
    if participant_dir == "PT":
        start_index = id.find('8247')
        return id[start_index:].strip()
    else:
        return id
    
def parse_task_df(df):
    task_cols = ['Participant Public ID', 'Participant Private ID', 'Task Name', 'Experiment Version', 'Trial Number', 'Reaction Time', 'Correct']

    # filter out unnecessary rows & select specific columns
    participant_data = df.loc[(df['Screen Name'] == 'test_sample') & (df['display'] == 'trial'), task_cols]

    # Reformat the Public ID values using the custom function - assuming at least one is incorrectly formatted
    participant_data['Participant Public ID'] = participant_data['Participant Public ID'].apply(lambda x: format_index(x))
    participant_data.set_index(id_cols, inplace=True)

    return participant_data.sort_index()

def main():
    exp_no = get_exp_no("C", participant_dir) #experiment number in Gorilla - used for naming the output files

    current_date = datetime.now().strftime("%Y_%m_%d") #for keeping track of when data files were generated
    suffix = "data_exp_"+exp_no+'-'+current_date
    save_dir = '../data/cleaned_data/'+participant_dir+'/'
    path_to_task_dir = '../data/raw_data/'+participant_dir+'/'

    task_df = gen_cleaned_task_data(parse_task_df, path_to_task_dir, "C - Delay Match to Sample")

    # writing C relevant dataframes to csv files
    task_df.to_csv(save_dir+'C-task_info-'+suffix+'.csv', index=True)
main()