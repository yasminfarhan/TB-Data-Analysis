import pandas as pd
import sys
from datetime import datetime
from utils import get_exp_no, gen_cleaned_task_data, q_map
from tb_q_processing import gen_mapped_scores, compute_scores

def parse_d_df(df):
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
    participant_data = participant_data.sort_values(by=['Participant Private ID', 'Level'])

    participant_data.set_index('Participant Private ID', inplace=True)

    return participant_data

def parse_d2_df(df):
    task_cols = ['Participant Private ID', 'Participant Public ID', 'Spreadsheet', 'Task Name', 'Experiment Version', 'Trial Number', 'Reaction Time', 'Response', 'EasyAmount']

    # filter out unnecessary rows then columns from this participant's data
    participant_data = df.loc[df['Screen Name'] == "offer", task_cols]

    participant_data.loc[participant_data['Spreadsheet'] == '1-vs-2-back', 'Spreadsheet'] = "2"
    participant_data.loc[participant_data['Spreadsheet'] == '1-vs-3-back', 'Spreadsheet'] = "3"
    participant_data.loc[participant_data['Spreadsheet'] == '1-vs-4-back', 'Spreadsheet'] = "4"
    participant_data.loc[participant_data['Spreadsheet'] == '1-vs-5-back', 'Spreadsheet'] = "5"
    participant_data.loc[participant_data['Spreadsheet'] == '1-vs-6-back', 'Spreadsheet'] = "6"

    # simplifying data
    participant_data.loc[participant_data['Response'] == '1-back-solid-fill.png', 'Response'] = 1
    participant_data.loc[participant_data['Response'].isin(['2-back-solid-fill.png', 
                                                    '3-back-solid-fill.png', 
                                                    '4-back-solid-fill.png', 
                                                    '5-back-solid-fill.png', 
                                                    '6-back-solid-fill.png']), 'Response'] = 0

    # renaming column
    participant_data = participant_data.rename(columns={'Response': 'IsEasy', 'Spreadsheet': 'Level'})
    participant_data = participant_data.sort_values(by=['Participant Private ID', 'Level'])

    participant_data.set_index('Participant Private ID', inplace=True)

    return participant_data

def parse_ntlx(df):
    # don't change anything - we're going to make use of the imported gen_mapped_scores, compute_scores for processing 
    df.set_index('Participant Private ID', inplace=True)

    return df

def gen_ntlx(df):
    scores = compute_scores(gen_mapped_scores({"NTLX": df}, q_map), q_map)
    dfs = []
    cols = ['NTLX_1', 'NTLX_2', 'NTLX_3', 'NTLX_4', 'NTLX_5', 'NTLX_6']

    # reformatting NTLX df so that there is only a single row per participant, and total NTLX scores as cols
    for pvid, ntlx_scores in scores.groupby('Participant Private ID'):
        ntlx_scores.set_index('Participant Private ID', inplace=True)
        ntlx_scores = ntlx_scores.transpose()
        ntlx_scores.columns = cols
        ntlx_scores.index = [pvid]

        dfs.append(ntlx_scores)
    all_scores = pd.concat(dfs, axis=0)

    return all_scores

def main():
    participant_dir = sys.argv[1] #PT or HC - i.e. Patient or Healthy Control directories
    exp_no = get_exp_no("D", participant_dir) #experiment number in Gorilla - used for naming the output files

    current_date = datetime.now().strftime("%Y_%m_%d") #for keeping track of when data files were generated
    suffix = "data_exp_"+exp_no+'-'+current_date
    save_dir = '../data/cleaned_data/'+participant_dir+'/'
    path_to_task_dir = '../data/raw_data/'+participant_dir+'/D/'

    d1_df = gen_cleaned_task_data(parse_d_df, path_to_task_dir, "D1 - N-Back Experience")
    d1_ntlx = gen_cleaned_task_data(parse_ntlx, path_to_task_dir, "NASA-TLX (NTLX)")
    d2_df = gen_cleaned_task_data(parse_d2_df, path_to_task_dir, "D2 - Effort Discounting - Trials")
    d3_df = gen_cleaned_task_data(parse_d_df, path_to_task_dir, "D3 - N-Back Task (1-back or 3-back)")

    # writing D relevant dataframes to csv files
    d1_df.to_csv(save_dir+'D1-task_info-'+suffix+'.csv', index=True)
    d2_df.to_csv(save_dir+'D2-task_info-'+suffix+'.csv', index=True)
    d3_df.to_csv(save_dir+'D3-task_info-'+suffix+'.csv', index=True)
    gen_ntlx(d1_ntlx).to_csv(save_dir+'D1-NTLX_info-'+suffix+'.csv', index=True)
    
main()