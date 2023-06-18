import pandas as pd
import sys
from datetime import datetime
from utils import get_exp_no, search_csv_files, concatenate_csv_files, gen_cleaned_task_data

# Task Name: 'Bv3 - Information Seeking Task - Varying Probability/Delay'
# Information we can get: 
# - quiz performance, i.e. how many tries until it took to pass, which questions were wrong
# - info seeking behavior
# - visual cue ratings 

# Parsing the Bv3 spreadsheet to obtain participant's information seeking behavior
def parse_task_df(df):
    task_cols = ['Participant Public ID', 'Participant Private ID', 'Task Name', 'Spreadsheet', 'Experiment Version', 'Trial Number', 'Reaction Time', 'Response', 'delay', 'reward_prob']

    # Filter rows based on conditions and select the 'Screen.Name' column
    outcome_column = df.loc[
        (df['Screen Name'] == 'reward_pos') |
        (df['Screen Name'] == 'reward_neg'),
        'Screen Name'].map({'reward_pos': 'Yes', 'reward_neg': 'No'}).reset_index(drop=True)
    
    # Filter rows based on conditions and select specific columns
    participant_data = df.loc[
        (df['Screen Name'] == 'offer_b') &
        (df['display'] == 'trial'),
        task_cols
    ].reset_index(drop=True)

    participant_data['GotReward'] = outcome_column
    participant_data.set_index('Participant Public ID', inplace=True)

    return participant_data.sort_index()

# Parsing the Bv3 spreadsheet to obtain participant's feeback following task
def parse_feedback_df(df):
    fb_cols = ['Participant Public ID', 'Participant Private ID', 'Task Name', 'Spreadsheet', 'Experiment Version', 'Screen Name', 'Response']

    # Filter rows based on conditions and select specific columns
    participant_data = df.loc[
        (df['display'] == 'end'),
        fb_cols
    ].reset_index(drop=True).dropna()
    participant_data.set_index('Participant Public ID', inplace=True)

    return participant_data.sort_index()

# searching, concatenating, and cleaning up reward questionnaire files
def cleanup_rwd_q(search_dir, task_name='Reward Questionnaire'):
    matching_files = search_csv_files(search_dir, "Task Name", task_name)

    # df with all unparsed task info across all participants
    rwd_df = concatenate_csv_files(matching_files)

    rwd_cols = ['Participant Public ID', 'Participant Private ID', 'Task Name', 'response-rank', 'response-animal', 'response-babies', 'response-other']
    
    # Filter rows based on conditions and select specific columns
    rwd_df = rwd_df.loc[:,
        rwd_cols
    ].reset_index(drop=True).dropna()
    rwd_df.set_index('Participant Public ID', inplace=True)

    return rwd_df.sort_index()

def main():
    participant_dir = sys.argv[1] #PT or HC - i.e. Patient or Healthy Control directories
    exp_no = get_exp_no("B", participant_dir) #experiment number in Gorilla - used for naming the output files

    current_date = datetime.now().strftime("%Y_%m_%d") #for keeping track of when data files were generated
    suffix = "data_exp_"+exp_no+'-'+current_date
    save_dir = '../data/cleaned_data/'+participant_dir+'/'
    path_to_task_dir = '../data/raw_data/'+participant_dir+'/'

    task_df = gen_cleaned_task_data(parse_task_df, path_to_task_dir, "Bv3 - Information Seeking Task - Varying Probability/Delay")
    fb_df = gen_cleaned_task_data(parse_feedback_df, path_to_task_dir, "Bv3 - Information Seeking Task - Varying Probability/Delay")
    rwd_df = cleanup_rwd_q(path_to_task_dir)

    # writing Bv3 relevant dataframes to csv files
    task_df.to_csv(save_dir+'Bv3-task_info-'+suffix+'.csv', index=True)
    fb_df.to_csv(save_dir+'Bv3-fb_info-'+suffix+'.csv', index=True)
    rwd_df.to_csv(save_dir+'Bv3-rwd_info-'+suffix+'.csv', index=True)
main()