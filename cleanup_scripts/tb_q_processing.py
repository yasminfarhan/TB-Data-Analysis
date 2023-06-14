import os
import pandas as pd
import csv
import pickle
import sys
from datetime import datetime

path_to_exp_dir = sys.argv[1]
incl_q = ["AUDIT", "BIS", "AES", "TEPS", "ASRS", "AQ", "OCI", "NCS", "STAI", "SDS", "LSAS", "EAT", "SSMS", "SPSRQ", "SHAPS"]
excl_col = ['Q_EAT_Current Weight']
# note - for SHAPS a higher score indicates higher anhedonia

# reading raw questionnaire files (as downloaded from Gorilla in short form) and aggregating them into a dict
def aggregate_questionnaires(cwd):
    q_dfs = {}

    for f in os.listdir(cwd):
        if "questionnaire" in f:
            with open(path_to_exp_dir+f, 'r') as q_file:
                reader = csv.reader(q_file)

                task_idx = next(reader).index("Task Name")
                first_row = next(reader)

                if len(first_row) > 1:
                    task = first_row[task_idx]
                    if any(item in task for item in incl_q):
                        q_acronym = task.split(' ')[-1][1:-1].split('-')[0].lower()
                        q_df = pd.read_csv(path_to_exp_dir+f)
                        
                        if(q_acronym == "oci"):
                            q_acronym = "ocir"

                        new_sheet_name = q_acronym.upper()

                        q_df.set_index('Participant Private ID', inplace=True)
                        q_dfs[new_sheet_name] = q_df.iloc[:-1,:].sort_index() #add this questionnaire to dict of all questionnaires

    return q_dfs

# generate a dictionary of questionnaire dataframes that include only the mapped questionnaire items
# put this in a separate function in case we ever want all individual questionnaire items and not just the totals
def gen_mapped_scores(_q_df_dict, _q_map):
    q_df_mapped_dict = {} 

    for q, q_df in _q_df_dict.items():
        q_key = q.split('_')[0].upper() #getting Q acronym
        q_cols = [col for col in q_df.columns if col.startswith('Q_') and 'quantised' not in col and 'text' not in col] #get only the numerical columns we want to include

        # new q_df with mapped scores
        q_df_mapped = pd.DataFrame()

        for col in q_cols:
            if "REV" in col:
                q_df_mapped[col] = q_df[col].map(_q_map[q_key]["REVERSED"]).fillna(q_df[col])
            else:
                if col == "Q_EAT_C3":
                    q_df_mapped[col] = q_df[col].map(_q_map[q_key]["NORMAL_C3"]).fillna(q_df[col])
                else:
                    q_df_mapped[col] = q_df[col].map(_q_map[q_key]["NORMAL"]).fillna(q_df[col])

        # add this questionnaires mapped scores to the df
        q_df_mapped_dict[q_key] = q_df_mapped

    return q_df_mapped_dict

# compute total & subscale scores for each questionnaire
def compute_scores(_q_df_mapped_dict, _q_map):
    df_scores = pd.DataFrame()

    for q, q_df in _q_df_mapped_dict.items():
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
def main():
    suffix = path_to_exp_dir.split('/')[-2] #sheet name, file suffix
    current_date = datetime.now().strftime("%Y_%m_%d") #for keeping track of when data files were generated

    # Read in questionnaire mapping dictionary
    with open('q_map.pkl', 'rb') as file:
        q_map = pickle.load(file)  

    q_dfs_aggr = aggregate_questionnaires(path_to_exp_dir) # aggregate raw questionnaires
    q_dfs_mapped = gen_mapped_scores(q_dfs_aggr, q_map) 
    df_scores = compute_scores(q_dfs_mapped, q_map)
    df_all_items = pd.DataFrame()

    # Loop through each dataframe in the dictionary and write it to a sheet in the Excel file
    with pd.ExcelWriter('../data/cleaned_data/'+current_date+'-q_aggregated_'+suffix+'.xlsx', engine='openpyxl') as writer:
        for sheet_name, df in q_dfs_aggr.items():
            df.to_excel(writer, sheet_name=sheet_name, index=False)

    # Write the mapped questionnaire items to an Excel file
    with pd.ExcelWriter('../data/cleaned_data/'+current_date+'-q_mapped_'+suffix+'.xlsx', engine='openpyxl') as writer:
        for sheet_name, df in q_dfs_mapped.items():
            df_all_items = pd.concat([df_all_items, df],axis=1)
            df = df.reset_index(drop=False)
            df.to_excel(writer, sheet_name=sheet_name, index=False)

    # Write all mapped questionnaire items to a single csv file
    df_all_items.reset_index(drop=False).to_csv('../data/cleaned_data/'+current_date+'-q_all_items_mapped_'+suffix+'.csv', index=False)

    # Write the computed questionnaire totals to a csv file
    df_scores.to_csv('../data/cleaned_data/'+current_date+'-q_scored_'+suffix+'.csv', index=False)
main()