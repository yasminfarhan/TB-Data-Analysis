import os
import pandas as pd
import csv
import pickle
import sys
from datetime import datetime
from utils import get_exp_no, search_csv_files, concatenate_csv_files, gen_cleaned_task_data

def parse_task_df(df):
    pass

def main():
    participant_dir = sys.argv[1] #PT or HC - i.e. Patient or Healthy Control directories
    exp_no = get_exp_no("A", participant_dir) #experiment number in Gorilla - used for naming the output files

    current_date = datetime.now().strftime("%Y_%m_%d") #for keeping track of when data files were generated
    suffix = "data_exp_"+exp_no+'-'+current_date
    save_dir = '../data/cleaned_data/'+participant_dir+'/'
    path_to_task_dir = '../data/raw_data/'+participant_dir+'/A/'

    task_df = gen_cleaned_task_data(parse_task_df, path_to_task_dir, "")

    # writing C relevant dataframes to csv files
    task_df.to_csv(save_dir+'A-task_info-'+suffix+'.csv', index=True)
main()