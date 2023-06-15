import os
import pandas as pd
import csv

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