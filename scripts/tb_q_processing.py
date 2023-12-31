import os
import pandas as pd
import csv
import sys
from datetime import datetime as dt
import datetime
from utils import get_exp_no, q_map, id_cols

incl_q = ["AUDIT", "BIS", "AES", "TEPS", "ASRS", "AQ", "OCI", "NCS", "STAI", "SDS", "LSAS", "EAT", "SSMS", "SPSRQ", "SHAPS", "Demographics"]
excl_col = ['Q_EAT_Current Weight']
# note - for SHAPS a higher score indicates higher anhedonia

#function to calculate age
def calculate_age(row):
    birth_month = row['Demo-Birthday-month']
    birth_day = row['Demo-Birthday-day']
    birth_year = row['Demo-Birthday-year']

    if birth_month == '' or birth_day == '' or birth_year == '':
        return float("nan")

    today = datetime.date.today()
    birth_date = datetime.date(int(birth_year), int(birth_month), int(birth_day))
    age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
    return age

# reading raw questionnaire files (as downloaded from Gorilla in short form) and aggregating them into a dict
def aggregate_questionnaires(cwd, dir):
    # id_string = 'Participant Private ID' if dir == "HC" else 'Participant Public ID'
    q_dfs = {}

    for root, dirs, files in os.walk(cwd):
        for f in files:
            if "questionnaire" in f:
                file_path = os.path.join(root, f)
                with open(file_path, 'r') as q_file:
                    reader = csv.reader(q_file)

                    task_idx = next(reader).index("Task Name")
                    first_row = next(reader)

                    if len(first_row) > 1:
                        task = first_row[task_idx]
                        if any(item in task for item in incl_q):
                            q_acronym = task.split(' ')[-1][1:-1].split('-')[0].upper() if task != "Demographics" else "DEMO"
                            q_df = pd.read_csv(file_path)
                            
                            if(q_acronym == "OCI"):
                                q_acronym = "OCIR"

                            q_df.set_index(id_cols, inplace=True)
                            q_dfs[q_acronym] = q_df.iloc[:-1,:].sort_index() #add this questionnaire to dict of all questionnaires

    return q_dfs

# generate a dictionary of questionnaire dataframes that include only the mapped questionnaire items
# put this in a separate function in case we ever want all individual questionnaire items and not just the totals
def gen_mapped_scores(_q_df_dict, _q_map):
    q_df_mapped_dict = {} 

    for q, q_df in _q_df_dict.items():
        q_key = q.split('_')[0].upper() #getting Q acronym
        start_string = "Q_" if q_key != "DEMO" else "Demo"
        q_df_mapped = pd.DataFrame() # new q_df with mapped scores

        q_cols = [col for col in q_df.columns if col.startswith(start_string) and 'quantised' not in col and 'text' not in col] #get only the numerical columns we want to include

        if q_key in _q_map.keys(): #is this a mappable questionnaire?
            for col in q_cols:
                if "REV" in col:
                    q_df_mapped[col] = q_df.loc[:, col].map(_q_map[q_key]["REVERSED"]).fillna(q_df[col])
                else:
                    if col == "Q_EAT_C3":
                        q_df_mapped[col] = q_df.loc[:, col].map(_q_map[q_key]["NORMAL_C3"]).fillna(q_df[col])
                    else:
                        q_df_mapped[col] = q_df.loc[:, col].map(_q_map[q_key]["NORMAL"]).fillna(q_df[col])
        else: #just save selected cols as is - this is Demographics questionnaire
            # replace birth month, day, year w/age
            q_df_mapped[q_cols] = q_df.loc[:, q_cols]

            if q_key == "DEMO":
                q_df_mapped["Demo-Age"] = q_df.apply(calculate_age, axis=1)

        # add this questionnaires mapped scores to the df
        q_df_mapped_dict[q_key] = q_df_mapped

    return q_df_mapped_dict

# compute total & subscale scores for each questionnaire
def compute_scores(_q_df_mapped_dict, _q_map):
    df_scores = pd.DataFrame()

    for q, q_df in _q_df_mapped_dict.items():
        if q in _q_map.keys(): #is this a score computable questionnaire?
            tot_col_name = "Q_"+q+"_TOT_SCORE"

            if "SUBSCALES" in _q_map[q].keys():
                for SS in _q_map[q]["SUBSCALES"]:
                    ss_col_name = "Q_"+q+"_"+SS+"_SCORE"

                    if q == "LSAS" or (q == "EAT" and SS == "C"): #there is no _ between SS and number, unlike other questionnaires, e.g. LSAS_A1 vs LSAS_A_1
                        ss_cols = [col for col in q_df.columns if SS in col.split('_')[-1] and col not in excl_col] 
                    else:
                        # get dataframe consisting only of subscale columns
                        ss_cols = [col for col in q_df.columns if SS in col.split('_') and col not in excl_col]

                    # extract a dataframe consisting of only the columns relevant to this subscale
                    ss_df = q_df.loc[:, ss_cols]

                    # add subscale column to df with all score sums
                    df_scores[ss_col_name] = ss_df.loc[:, list(ss_df.columns)].sum(axis=1, numeric_only=True)

                # compute total q score using ss scores
                df_scores[tot_col_name] = df_scores.filter(like="Q_"+q).sum(axis=1, numeric_only=True) 
            else:
                df_scores[tot_col_name] = q_df.sum(axis=1, numeric_only=True)

    return df_scores.reset_index(drop=False)    


# TO RUN: pass in the path to the experiment directory as downloaded to Gorilla as second arg in command line - e.g. python tb_q_processing.py path/to/dir/
if __name__ == "__main__":
    participant_dir = sys.argv[1] #PT or HC - i.e. Patient or Healthy Control directories
    exp_no = get_exp_no("Q", participant_dir) #experiment number in Gorilla - used for naming the output files

    current_date = dt.now().strftime("%Y_%m_%d") #for keeping track of when data files were generated
    suffix = "data_exp_"+exp_no+'-'+current_date
    save_dir = '../data/cleaned_data/'+participant_dir+'/'
    path_to_q_dir = '../data/raw_data/'+participant_dir+'/'

    q_dfs_aggr = aggregate_questionnaires(path_to_q_dir, participant_dir) # aggregate raw questionnaires
    q_dfs_mapped = gen_mapped_scores(q_dfs_aggr, q_map) 
    df_scores = compute_scores(q_dfs_mapped, q_map)
    df_all_items = pd.DataFrame()

    # Loop through each dataframe in the dictionary and write it to a sheet in the Excel file
    with pd.ExcelWriter(save_dir+'Q_aggregated-'+suffix+'.xlsx', engine='openpyxl') as writer:
        for sheet_name, df in q_dfs_aggr.items():
            df.to_excel(writer, sheet_name=sheet_name, index=False)

    # Write the mapped questionnaire items to an Excel file
    with pd.ExcelWriter(save_dir+'Q_mapped-'+suffix+'.xlsx', engine='openpyxl') as writer:
        for sheet_name, df in q_dfs_mapped.items():
            if sheet_name == "DEMO":
                df.to_csv(save_dir+'DEMO-'+suffix+'.csv', index=True)
            else:
                df_all_items = pd.concat([df_all_items, df],axis=1)
            df = df.reset_index(drop=False)
            df.to_excel(writer, sheet_name=sheet_name, index=False)

    # Write all mapped questionnaire items to a single csv file
    df_all_items.reset_index(drop=False).to_csv(save_dir+'Q_all_items_mapped-'+suffix+'.csv', index=False)

    # Write the computed questionnaire totals to a csv file
    df_scores.to_csv(save_dir+'Q_scored-'+suffix+'.csv', index=False)
