import os
import pandas as pd
import csv

id_cols = 'Participant Public ID' #if you want multi-index, reformat as list

latest_exp_no_dict = {
    "PT": {"A": "122902",
           "B": "129671",
           "C": "129672",
           "D": "94072",
           "Q": "127044"},
    "HC": {"A": "96014", #NOTE: they are all the same for HC bc Prolific experiment includes all tasks
           "B": "96014",
           "C": "96014",
           "D": "96014",
           "Q": "96014"},
}

q_map = {

  "AUDIT" : {
             "NORMAL": {"Never": 0,
                    "Less than Monthly": 1,
                    "Monthly": 2,
                    "Weekly": 3,
                    "Almost Daily": 4,
                    "Daily": 5,
                    "No": 0,
                    "Yes - but not in the last year": 2,
                    "Yes - during the last year": 4,
                    "0": 0,
                    "1 or 2": 1,
                    "3 or 4": 2,
                    "5 or 6": 3,
                    "7 to 9": 4,
                    "10 or more": 5}
            },
  "AES"  : {
            "NORMAL": {"Very True": 1,
                       "Somewhat True": 1,
                       "Slightly True": 3,
                       "Not at All True": 4}, 
            "REVERSED": {"Very True": 4,
                       "Somewhat True": 3,
                       "Slightly True": 1,
                       "Not at All True": 1},
            "SUBSCALES": ["C", "B", "E"]
            },
  "ASRS"  : {
            "NORMAL": {"Never": 0,
                       "Rarely": 1,
                       "Sometimes": 2,
                       "Often": 3,
                       "Very Often": 4}, 
            },
  "AQ"   : {
            "NORMAL": {"Definitely Disagree": 0,
                       "Slightly Disagree": 0,
                       "Slightly Agree": 1,
                       "Definitely Agree": 1}, 
            "REVERSED": {"Definitely Disagree": 1,
                        "Slightly Disagree": 1,
                        "Slightly Agree": 0,
                        "Definitely Agree": 0}
            },
  "BIS"  : {
            "NORMAL": {"1": 1,
                       "2": 2,
                       "3": 3,
                       "4": 4}, 
            },
  "EAT"  : {
            "NORMAL": {"Never": 0,
                       "Rarely": 0,
                       "Sometimes": 0,
                       "Often": 1,
                       "Usually": 2,
                       "Always": 3,
                       "Once a month or less": 0,
                       "2-3 times a month": 1,
                       "Once a week": 1,
                       "2-6 times a week": 1,
                       "Once a day or more": 1,
                       "No": 0,
                       "Yes": 1,
                       },
            "NORMAL_C3": {"Never": 0,
                       "Once a month or less": 1,
                       "2-3 times a month": 1,
                       "Once a week": 1,
                       "2-6 times a week": 1,
                       "Once a day or more": 1,
                       },
            "SUBSCALES": ["DI", "BU", "OC", "C"] 
            },
  "NTLX" : {
            "NORMAL": {"1": 1,
                       "2": 2,
                       "3": 3,
                       "4": 4,
                       "5": 5}, 
            "REVERSED": {"1": 5,
                         "2": 4,
                         "3": 3,
                         "4": 2,
                         "5": 1}
            },
  "NCS"  : {
            "NORMAL": {"1": 1,
                       "2": 2,
                       "3": 3,
                       "4": 4,
                       "5": 5}, 
            "REVERSED": {"1": 5,
                         "2": 4,
                         "3": 3,
                         "4": 2,
                         "5": 1}
            },
  "OCIR"  : {
            "NORMAL": {"0": 0,
                       "1": 1,
                       "2": 2,
                       "3": 3,
                       "4": 4}
            },
  "SDS"  : {
            "NORMAL": {"A Little of the Time": 1,
                       "Some of the Time": 2,
                       "Good Part of the Time": 3,
                       "Most of the Time": 4}, 
            "REVERSED": {"A Little of the Time": 4,
                         "Some of the Time": 3,
                         "Good Part of the Time": 2,
                         "Most of the Time": 1}
            },
  "SPSRQ" : {
            "NORMAL": {"Yes": 1,
                       "No": 0},
             "SUBSCALES": ["P", "R"] 
            },
  "SSMS" : {
            "NORMAL": {"Yes": 1,
                       "No": 0}, 
            "REVERSED": {"Yes": 0,
                         "No": 1},
            "SUBSCALES": ["UE", "CD", "A", "IN"]},
  "SHAPS" : {
            "NORMAL": {"Strongly disagree": 1,
                       "Disagree": 1,
                       "Agree": 0,
                       "Definitely agree": 0}, 
            },
  "STAI" : {
            "NORMAL": {"1": 1,
                       "2": 2,
                       "3": 3,
                       "4": 4}, 
            "REVERSED": {"1": 4,
                         "2": 3,
                         "3": 2,
                         "4": 1},
            "SUBSCALES": ["S", "T"]
            },
  "LSAS" : {
            "NORMAL": {"0": 0,
                       "1": 1,
                       "2": 2,
                       "3": 3},
            "SUBSCALES": ["F", "A"] 
            },
  "TEPS" : {
            "NORMAL": {"Very false for me": 1,
                       "Moderately false for me": 2,
                       "Slightly false for me": 3,
                       "Slightly true for me": 4,
                       "Moderately true for me": 5,
                       "Very true for me": 6}, 
            "REVERSED": {"Very false for me": 6,
                       "Moderately false for me": 5,
                       "Slightly false for me": 4,
                       "Slightly true for me": 3,
                       "Moderately true for me": 2,
                       "Very true for me": 1},
            "SUBSCALES": ["ANT", "CON"]
            },
}

def get_exp_no(task_id, p_type):
    return latest_exp_no_dict[p_type][task_id]

# searching across all directories for files that are relevant for the task we're looking for
def search_csv_files(directory, column_name, search_string):
    csv_files = []
    
    for root, dirs, files in os.walk(directory):
        for filename in files:
            if filename.endswith(".csv"):
                file_path = os.path.join(root, filename)
                with open(file_path, 'r') as file:
                    reader = csv.reader(file)
                    first_row = next(reader)
                    if column_name in first_row:
                        column_index = first_row.index(column_name)
                        for row in reader:
                            if column_index < len(row) and row[column_index] == search_string:
                                csv_files.append(file_path)
                                break
    
    return csv_files

# concatenating all relevant csv files (across task versions, branches) into one
def concatenate_csv_files(file_paths):
    dataframes = []
    
    for file_path in file_paths:
        df = pd.read_csv(file_path)
        dataframes.append(df)
    
    concatenated_df = pd.concat(dataframes, axis=0, ignore_index=True)
    return concatenated_df 

# parsing and concatenating pd dataframes on the level of the participant
def gen_cleaned_task_data(parse_df, search_dir, task_name): #parse_df is a func with an implementation unique to cleanup script passing it in
    matching_files = search_csv_files(search_dir, "Task Name", task_name)
    all_id_df = pd.DataFrame() # a dataframe containing the task info for all participants

    if len(matching_files):
        # df with all unparsed task info across all participants
        task_df = concatenate_csv_files(matching_files)[:-1] #up until last row if last row is all NaN

        for _, group in task_df.groupby('Participant Private ID'):
            parsed_df = parse_df(group)
            all_id_df = pd.concat([all_id_df, parsed_df], axis=0)
    else:
        print("No relevant task files were found.")
    return all_id_df.sort_index()