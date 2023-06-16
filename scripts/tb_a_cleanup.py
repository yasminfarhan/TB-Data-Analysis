import pandas as pd
import sys
from datetime import datetime
from utils import get_exp_no, search_csv_files, concatenate_csv_files, gen_cleaned_task_data

def parse_task_df(df):
    task_a_cols = ['Participant Public ID', 'Participant Private ID', 'Task Name', 'Spreadsheet', 'Trial Number', 'Reaction Time', 'Response', 'deck_a_p', 'deck_b_p', 'deck_c_p']

    # filter out rows which only have the win/lose outcome information per trial, then select that column
    outcome_column = df.loc[((df['Zone Type'] != "timelimit_screen") & (df['display'] == "trial")) 
                                        & ((df['Screen Name'] == "win") | (df['Screen Name'] == "lose")) , 'Screen Name']

    # now that we have outcome information, filter out unnecessary rows then columns from this participant's data
    participant_data = df.loc[(df['Screen Name'] == "offer") & (df['display'] == "trial"), task_a_cols]

    # adding outcome column to participant df - reset index first so it is added correctly
    outcome_column = outcome_column.reset_index(drop=True)
    participant_data = participant_data.reset_index(drop=True)
    participant_data['Outcome'] = outcome_column

    # replacing Deck image name with A,B,C for simpler interpretation
    participant_data.loc[participant_data['Response'] == 'Deck A.png', 'Response'] = 'A'
    participant_data.loc[participant_data['Response'] == 'Deck B.png', 'Response'] = 'B'
    participant_data.loc[participant_data['Response'] == 'Deck C.jpg', 'Response'] = 'C'

    # truncating spreadsheet type
    participant_data.loc[participant_data['Spreadsheet'] == 'fixed_probabilities_full', 'Spreadsheet'] = 'fixed'
    participant_data.loc[participant_data['Spreadsheet'] == 'volatile_probabilities_full', 'Spreadsheet'] = 'volatile'
    participant_data.loc[participant_data['Task Name'] == 'Av1 - 3 Arm Bandit - NoWin/Loss', 'Task Name'] = 'nowin/loss'
    participant_data.loc[participant_data['Task Name'] == 'Av2 - 3 Arm Bandit - Win/Loss', 'Task Name'] = 'win/loss'
    participant_data.loc[participant_data['Task Name'] == 'Av3 - 3 Arm Bandit - Win/NoLoss', 'Task Name'] = 'win/noloss'

    # renaming column
    participant_data = participant_data.rename(columns={'Spreadsheet': 'Probabilities', 'Task Name': 'Task Type'})
    participant_data.set_index('Participant Private ID', inplace=True)

    return participant_data

def parse_feedback_df():
    # # filter out rows which have the feedback participants gave about how they're feeling & their probability estimate for each deck + confidence level
    # participant_feedback = df.loc[df['Zone.Type'] == "response_rating_scale_likert",
    #                                             ['Participant.Private.ID', 'Task.Name', 'Spreadsheet', 'Screen.Name', 'display', 'Trial.Number', 'Response']]
    pass

def main():
    participant_dir = sys.argv[1] #PT or HC - i.e. Patient or Healthy Control directories
    exp_no = get_exp_no("A", participant_dir) #experiment number in Gorilla - used for naming the output files

    current_date = datetime.now().strftime("%Y_%m_%d") #for keeping track of when data files were generated
    suffix = "data_exp_"+exp_no+'-'+current_date
    save_dir = '../data/cleaned_data/'+participant_dir+'/'
    path_to_task_dir = '../data/raw_data/'+participant_dir+'/A/'

    task_df_av1 = gen_cleaned_task_data(parse_task_df, path_to_task_dir, 'Av1 - 3 Arm Bandit - NoWin/Loss')
    task_df_av3 = gen_cleaned_task_data(parse_task_df, path_to_task_dir, 'Av3 - 3 Arm Bandit - Win/NoLoss')

    # writing A relevant dataframes to csv files
    task_df_av1.to_csv(save_dir+'Av1-task_info-'+suffix+'.csv', index=True)
    task_df_av3.to_csv(save_dir+'Av3-task_info-'+suffix+'.csv', index=True)
main()