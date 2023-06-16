import pandas as pd
import sys
from datetime import datetime
from utils import get_exp_no, gen_cleaned_task_data

def parse_d1_df(df):
    task_cols = ['Participant Private ID', 'Participant Public ID', 'Spreadsheet', 'Task Name', 'Experiment Version', 'Trial Number', 'Timed Out', 'Reaction Time', 'Response', 'Correct', 'Answer']

    # filter out unnecessary rows then columns from this participant's data
    participant_data = df.loc[df['Screen Name'] == "Trials", task_cols]

    # simplifying data
    participant_data.loc[participant_data['Answer'] == 'No-Button.png', 'Answer'] = 0
    participant_data.loc[participant_data['Answer'] == 'Yes-Button.png', 'Answer'] = 1
    participant_data.loc[participant_data['Response'] == 'No-Button.png', 'Response'] = 'No'
    participant_data.loc[participant_data['Response'] == 'Yes-Button.png', 'Response'] = 'Yes'

    # renaming column
    participant_data = participant_data.rename(columns={'Answer': 'IsTarget', 'Spreadsheet': 'Level'})
    participant_data.set_index('Participant Private ID', inplace=True)

    return participant_data

def main():
    participant_dir = sys.argv[1] #PT or HC - i.e. Patient or Healthy Control directories
    exp_no = get_exp_no("D", participant_dir) #experiment number in Gorilla - used for naming the output files

    current_date = datetime.now().strftime("%Y_%m_%d") #for keeping track of when data files were generated
    suffix = "data_exp_"+exp_no+'-'+current_date
    save_dir = '../data/cleaned_data/'+participant_dir+'/'
    path_to_task_dir = '../data/raw_data/'+participant_dir+'/D/'

    task_df = gen_cleaned_task_data(parse_d1_df, path_to_task_dir, "D1 - N-Back Experience")

    # writing D relevant dataframes to csv files
    task_df.to_csv(save_dir+'D1-task_info-'+suffix+'.csv', index=True)
main()