import pandas as pd
import numpy as np
from collections import defaultdict
import sys 
from datetime import datetime
from utils import get_exp_no

# a function to retrieve the number of times response == 'find out now' in the passed in dataframe under some delay and/or prob condition
def get_info_seeking_count(df, delay=None, prob=None):
  if delay is not None and prob is not None:
    return df[(df['Response'] == "find-out-now.png") & (df['delay'] == delay) & (df['reward_prob'] == prob)].shape[0]
  elif delay is not None:
    return df[(df['Response'] == "find-out-now.png") & (df['delay'] == delay)].shape[0]
  elif prob is not None:
    return df[(df['Response'] == "find-out-now.png") & (df['reward_prob'] == prob)].shape[0]

# function to add task b features to participant dictionary using data, feedback dataframes
def add_task_b_features(data_df, fb_df, rwd_df, p_dict):
    # get list of unique participant ids
    participant_ids = data_df.index.unique().tolist()
    
    # iterate through participant ids, getting the info we need per participant and adding to participant dict
    for id in participant_ids:
        print("\n", id)
        participant_fb_df = fb_df.loc[id] # this returns feedback info for this participant
        participant_data_df = data_df.loc[id].tail(44) # this returns a 25x6 df reflecting the 25 (or 44) trials and 6 columns (Trial.Number, Timed.Out, Reaction.Time, Response, delay, GotReward) for this participant id
        participant_rwd_df = rwd_df.loc[id]

############## reward questionnaire data ##############
        category_map = {"animals": "animal", "babies": "babies", "oddly satisfying": "other"}

        top_ranked_category = category_map[participant_rwd_df['response-rank'].lower()]
        p_dict[id]["B_PRE_RWD_CATEGORY"] = top_ranked_category
        p_dict[id]["B_PRE_RWD_RATING"] = participant_rwd_df['response-'+top_ranked_category]

        # adding rankings for all categories
        for category in category_map.values():
           p_dict[id]["B_"+category.upper()+"_RATING"] = participant_rwd_df['response-'+category]
                   
############## task data ##############################
        # Compute Average Reaction Time (ART)
        p_dict[id]["B_ART"] = participant_data_df['Reaction Time'].astype(float).mean()

        # PROPORTION_FON - Compute proportion of rows where 'Response' is 'find out now' across all delay/prob conditions
        p_dict[id]["B_PROP_FON"] = (participant_data_df[(participant_data_df['Response'] == "find-out-now.png")].shape[0])/participant_data_df.shape[0]

        # Computing more granular FON proportions
        probs = sorted(data_df["reward_prob"].unique().tolist()) #depending on the version of the task, we may have >1 probability condition
        delays = sorted(data_df["delay"].unique().tolist())

        # PROP FON across delay conditions 
        for dly in delays:
            ft_name = "B_PROP_FON_CHOICE_{}s".format(str(int(dly))[:-3])

            # Compute the proportion of rows where 'Response' is equal to "find-out-now.png" and 'Delay' is equal to cur delay, add to dict
            p_dict[id][ft_name] = get_info_seeking_count(participant_data_df, delay=dly)/(participant_data_df[participant_data_df['delay'] == dly].shape[0])
            
        # PROP FON across prob conditions 
        for prb in probs:
            ft_name = "B_PROP_FON_CHOICE_{}p".format(str(prb).split(".")[1])

            # Compute the proportion of rows where 'Response' is equal to "find-out-now.png" and 'reward_prob' is equal to cur prb, add to dict
            p_dict[id][ft_name] = get_info_seeking_count(participant_data_df, prob=prb)/(participant_data_df[participant_data_df['reward_prob'] == prb].shape[0])

        if(len(probs) > 1 and len(delays) > 1):
            for prob in probs:
                for delay in delays:
                    key = "B_PROP_FON_CHOICE_{}_{}".format(str(int(delay))[:-3], str(prob).split(".")[1]) #B_NUM_FON_CHOICE_DELAY_PROB format

                    num = get_info_seeking_count(participant_data_df, delay, prob)
                    denom = participant_data_df[(participant_data_df['delay'] == delay) & (participant_data_df['reward_prob'] == prob)].shape[0]

                    p_dict[id][key] = num/denom

############## feedback data ##########################

        # AVG CUE RATING - Compute the average rating given across the three neutral cues (Apple, Ladder, Car) after having completed all trials
        p_dict[id]["B_AVG_CUE_RATING"] = participant_fb_df[participant_fb_df['Screen Name'].str.contains("cue")]['Response'].astype(float).mean()    

        # POST RWD RATING - Participant's rating of the reward videos overall AFTER having completed all trials
        p_dict[id]["B_POST_RWD_RATING"] = participant_fb_df.loc[participant_fb_df['Screen Name'] == "reward_rate", 'Response'].astype(float).iloc[0]

        # STATIC RATING - Participant's rating of the static video after having completed all trials
        p_dict[id]["B_STATIC_RATING"] = participant_fb_df.loc[participant_fb_df['Screen Name'] == "static_rate", 'Response'].astype(float).iloc[0]

############## interactions ###########################

        # Multiply reward rating by info seeking behavior - used in mixed effects modeling
        p_dict[id]['B_RVxPROP_FON'] = p_dict[id]['B_POST_RWD_RATING']*p_dict[id]['B_PROP_FON']

def process_task_b(exp_no, dir, save=True):
    current_date = datetime.now().strftime("%Y_%m_%d") #this assumes the files we're reading from were generated today
    suffix = "data_exp_"+exp_no+'-'+current_date
    save_dir = '../data/cleaned_data/'+dir+'/'

    ft_dict = defaultdict(defaultdict)

    df_data = pd.read_csv(save_dir+'Bv3-task_info-'+suffix+'.csv').set_index('Participant Public ID')
    df_fb = pd.read_csv(save_dir+'Bv3-fb_info-'+suffix+'.csv').set_index('Participant Public ID')
    df_rwd = pd.read_csv(save_dir+'Bv3-rwd_info-'+suffix+'.csv').set_index('Participant Public ID')

    add_task_b_features(df_data, df_fb, df_rwd, ft_dict)

    if save: # if we choose to save task B feature info in an independent file
       pd.DataFrame.from_dict(ft_dict, orient='index').to_csv(save_dir+'Bv3_FT_INFO-'+suffix+'.csv')

def main():
    p_dir = sys.argv[1] #PT or HC - i.e. Patient or Healthy Control directories
    ft_dict = process_task_b(get_exp_no("B", p_dir), p_dir)
main()