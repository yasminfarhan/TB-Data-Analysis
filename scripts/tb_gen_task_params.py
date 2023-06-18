import pandas as pd
from collections import defaultdict
import sys 
from datetime import datetime
from utils import get_exp_no

# function to add task a features to participant dictionary using data, feedback dataframes
def add_task_a_features(data_df, fb_df, p_dict, version):
  
    # get list of unique participant ids
    participant_ids = data_df.index.unique().tolist()
    
    if "volatile" in data_df['Probabilities'].iloc[0]:
        a_actual_prob = b_actual_prob = c_actual_prob = data_df[['deck_a_p', 'deck_b_p', 'deck_c_p']].iloc[0].mean()*100 #average of first row's probabilities - should always be some combo of these
    else: #fixed probabilities
        a_actual_prob = data_df['deck_a_p'].iloc[0]*100
        b_actual_prob = data_df['deck_b_p'].iloc[0]*100
        c_actual_prob = data_df['deck_c_p'].iloc[0]*100

    # iterate through participant ids, getting the info we need per participant and adding to participant dict
    for id in participant_ids:
            participant_data_df = data_df.loc[id] # this returns a num_trialsx10 df 
            participant_fb_df = fb_df.loc[id] # this returns feedback info for this participant

            ###### task data ######
            # get accuracy for this participant - i.e. the number of times within the 99 trials that this participant chose the deck with highest probability of reward/no loss
            num_correct = 0
            for i in range(participant_data_df.shape[0]):
                rsp = participant_data_df['Response'][i].lower()
                rsp_prob = participant_data_df['deck_'+rsp+'_p'][i]

                if rsp_prob == max([participant_data_df['deck_a_p'][i], participant_data_df['deck_b_p'][i], participant_data_df['deck_c_p'][i]]):
                    num_correct += 1

            # add accuracy to dict
            p_dict[id]['A'+version+'_ACC'] = num_correct/participant_data_df.shape[0]

            # get avg reaction time for this participant, and add to dict
            avg_rt = participant_data_df['Reaction Time'].astype(float).mean()
            p_dict[id]['A'+version+'_ART'] = avg_rt

            ##### feedback data ######
            participant_fb_df.loc[:,'Response'] = participant_fb_df['Response'].replace('', '0').astype(float) # convert response to float

            # calculate average mid_feedback, add to dict
            grouped_fb_df = participant_fb_df.groupby('display')['Response'].mean()
            p_dict[id]['A'+version+'_AVG_MF'] = grouped_fb_df['mid_feedback']

            # calculate average confidence, add to dict
            avg_prob_conf = participant_fb_df.groupby(participant_fb_df['Screen Name'].str.contains('conf')).get_group(True)['Response'].astype(float).mean()
            p_dict[id]['A'+version+'_AVG_PROB_CONF'] = avg_prob_conf

            # calculate deck a, b, c prob estimate accuracy, add to dict
            deck_a_prob_err_pct = (abs(participant_fb_df.loc[participant_fb_df['Screen Name'] == 'deck_a_prob', 'Response'].values[0]-a_actual_prob)/a_actual_prob)*100
            deck_b_prob_err_pct = (abs(participant_fb_df.loc[participant_fb_df['Screen Name'] == 'deck_b_prob', 'Response'].values[0]-b_actual_prob)/b_actual_prob)*100
            deck_c_prob_err_pct = (abs(participant_fb_df.loc[participant_fb_df['Screen Name'] == 'deck_c_prob', 'Response'].values[0]-c_actual_prob)/c_actual_prob)*100

            p_dict[id]['A'+version+'_A_PROB_ERR_PCT'] = deck_a_prob_err_pct
            p_dict[id]['A'+version+'_B_PROB_ERR_PCT'] = deck_b_prob_err_pct
            p_dict[id]['A'+version+'_C_PROB_ERR_PCT'] = deck_c_prob_err_pct

            if(version == "V3"):
                p_dict[id]['AV3_V1_DIFF_ABS'] = abs(p_dict[id]['AV3_ACC'] - p_dict[id]['AV1_ACC'])
                p_dict[id]['AV3_V1_DIFF_SIGN'] = (p_dict[id]['AV3_ACC'] - p_dict[id]['AV1_ACC'])

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
        # CUE RATING - save rating for each of the three neutral cues (Apple, Ladder, Car) after having completed all trials
        for cue in ["A", "B", "C"]:
            p_dict[id]["B_CUE_{}_RATING".format(cue)] = participant_fb_df[participant_fb_df['Screen Name'].str.contains("cue{}".format(cue))]['Response'][0]

        # AVG CUE RATING - Compute the average rating given across the three neutral cues (Apple, Ladder, Car) after having completed all trials
        p_dict[id]["B_AVG_CUE_RATING"] = participant_fb_df[participant_fb_df['Screen Name'].str.contains("cue")]['Response'].astype(float).mean()    

        # POST RWD RATING - Participant's rating of the reward videos overall AFTER having completed all trials
        p_dict[id]["B_POST_RWD_RATING"] = participant_fb_df.loc[participant_fb_df['Screen Name'] == "reward_rate", 'Response'].astype(float).iloc[0]

        # STATIC RATING - Participant's rating of the static video after having completed all trials
        p_dict[id]["B_STATIC_RATING"] = participant_fb_df.loc[participant_fb_df['Screen Name'] == "static_rate", 'Response'].astype(float).iloc[0]

############## interactions ###########################

        # Multiply reward rating by info seeking behavior - used in mixed effects modeling
        p_dict[id]['B_RVxPROP_FON'] = p_dict[id]['B_POST_RWD_RATING']*p_dict[id]['B_PROP_FON']

def add_task_c_features(data_df, p_dict):

    # get list of unique participant ids
    participant_ids = data_df.index.unique().tolist()

    # iterate through participant ids, getting the info we need per participant and adding to participant dict
    for id in participant_ids:
        participant_data_df = data_df.loc[id] 

        # Compute Average Reaction Time (ART), add to dict
        p_dict[id]["C_ART"] = participant_data_df['Reaction Time'].astype(float).mean()

        # C_ACC - Compute accuracy by counting number of rows where 'Correct' == 1
        p_dict[id]["C_ACC"] = (participant_data_df[(participant_data_df['Correct'].astype(float) == 1)].shape[0])/participant_data_df.shape[0] #divide by num trials

# function to retrieve the 1st half of each N-Back run if long version for fair acc comparison w/participants who did the short version
def get_short_nback(df, trials_per_run=64):
    if(df.shape[0] == trials_per_run*2): #long v
        # Retrieve the first half of the first run
        first_section = df[:trials_per_run // 2]

        # Retrieve the first half of the second run
        second_section = df[trials_per_run:trials_per_run + trials_per_run // 2]

        # Concatenate the two sections together
        new_df = pd.concat([first_section, second_section])

        # Reset the index of the new DataFrame
        new_df = new_df.reset_index(drop=True)

        return new_df
    else: #short version, needs no modifications
        return df

def add_task_d_features(df_d1_data, df_d1_ntlx, df_d2_data, df_d3_data, p_dict):
    # get list of unique participant ids
    participant_ids = df_d1_data.index.unique().tolist()
    ntlx_dict = df_d1_ntlx.to_dict('index')

    # iterate through participant ids, getting the info we need per participant and adding to participant dict
    for id in participant_ids:        
        p_d1 = df_d1_data.loc[id]
        p_d2 = df_d2_data.loc[id] 
        p_d3 = df_d3_data.loc[id] 

    ### D1 ###################
        p_dict[id]["D1_NUM_TIMEOUTS"] = p_d1[p_d1['Timed Out'] == 1].shape[0]

        # generate D1_1B_TGT_ACC, D1_2B_TGT_ACC, D1_3B_TGT_ACC, D1_4B_TGT_ACC, D1_5B_TGT_ACC, D1_6B_TGT_ACC, add to participant dict
        for i in range(1,7):
            d1_lvl = get_short_nback(p_d1[p_d1['Level'].str.startswith(str(i)+'-Back')]) #we want to compare the short/long versions appropriately, so take only the 1st half of each of the 2 runs (64 tot)
            d1_lvl_tot_tgt = d1_lvl[d1_lvl['IsTarget'].astype(float) == 1].shape[0]
            d1_lvl_tot_nontgt = d1_lvl[d1_lvl['IsTarget'].astype(float) == 0].shape[0]

            p_dict[id]["D1_"+str(i)+"B_TGT_ACC"] = d1_lvl[(d1_lvl['Correct'].astype(float) == 1) & (d1_lvl['IsTarget'].astype(float) == 1)].shape[0]/d1_lvl_tot_tgt
            p_dict[id]["D1_"+str(i)+"B_NON_TGT_ACC"] = d1_lvl[(d1_lvl['Correct'].astype(float) == 1) & (d1_lvl['IsTarget'].astype(float) == 0)].shape[0]/d1_lvl_tot_nontgt

        ### updating p_dict with NTLX values
        for ntlx_key, ntlx_score in ntlx_dict[id].items():
            p_dict[id][ntlx_key] = ntlx_score

    ### D2 ###################
        # generate features per decision level (1v2, 1v3, etc) and add to participant dict
        for i in range(2,7):
            str_prefix = "D2_1V"+str(i) 

            # retrieve the final easy choice ('IsEasy') and final easy amount ('EasyAmount') at trial 6
            p_dict[id][str_prefix+"_ISEASY"] = p_d2[p_d2['Level'] == i]['IsEasy'].astype(float).iloc[5]
            p_dict[id][str_prefix+"_EA"] = p_d2[p_d2['Level'] == i]['EasyAmount'].astype(float).iloc[5]

            # average reaction time at this level
            p_dict[id][str_prefix+"_ART"] = p_d2[p_d2['Level'] == i]['Reaction Time'].astype(float).mean()

    ### D3 ################### - generate proportion of timeouts, target accuracy
        p_dict[id]["D3_NUM_TIMEOUTS"] = p_d3[p_d3['Timed Out'] == 1].shape[0]
        print(id, p_dict[id]["D3_NUM_TIMEOUTS"])
        p_dict[id]["D3_TGT_ACC"] = p_d3[(p_d3['Correct'].astype(float) == 1) & (p_d3['IsTarget'].astype(float) == 1)].shape[0]/p_d3[(p_d3['IsTarget'].astype(float) == 1)].shape[0]
        p_dict[id]["D3_NON_TGT_ACC"] = p_d3[(p_d3['Correct'].astype(float) == 1) & (p_d3['IsTarget'].astype(float) == 0)].shape[0]/p_d3[(p_d3['IsTarget'].astype(float) == 0)].shape[0]

######## PROCESSING FUNCS
def process_task_a(exp_no, dir, ft_dict):
    current_date = datetime.now().strftime("%Y_%m_%d") #this assumes the files we're reading from were generated today
    suffix = "data_exp_"+exp_no+'-'+current_date
    read_dir = '../data/cleaned_data/'+dir+'/'
    
    # Av1
    df_data_av1 = pd.read_csv(read_dir+'Av1-task_info-'+suffix+'.csv').set_index('Participant Public ID')
    df_fb_av1 = pd.read_csv(read_dir+'Av1-fb_info-'+suffix+'.csv').set_index('Participant Public ID')

    # Av3
    df_data_av3 = pd.read_csv(read_dir+'Av3-task_info-'+suffix+'.csv').set_index('Participant Public ID')
    df_fb_av3 = pd.read_csv(read_dir+'Av3-fb_info-'+suffix+'.csv').set_index('Participant Public ID')

    add_task_a_features(df_data_av1, df_fb_av1, ft_dict, "V1")
    add_task_a_features(df_data_av3, df_fb_av3, ft_dict, "V3")

def process_task_b(exp_no, dir, ft_dict):
    current_date = datetime.now().strftime("%Y_%m_%d") #this assumes the files we're reading from were generated today
    suffix = "data_exp_"+exp_no+'-'+current_date
    read_dir = '../data/cleaned_data/'+dir+'/'

    df_data = pd.read_csv(read_dir+'Bv3-task_info-'+suffix+'.csv').set_index('Participant Public ID')
    df_fb = pd.read_csv(read_dir+'Bv3-fb_info-'+suffix+'.csv').set_index('Participant Public ID')
    df_rwd = pd.read_csv(read_dir+'Bv3-rwd_info-'+suffix+'.csv').set_index('Participant Public ID')

    add_task_b_features(df_data, df_fb, df_rwd, ft_dict)

def process_task_c(exp_no, dir, ft_dict):
    current_date = datetime.now().strftime("%Y_%m_%d") #this assumes the files we're reading from were generated today
    suffix = "data_exp_"+exp_no+'-'+current_date
    read_dir = '../data/cleaned_data/'+dir+'/'

    df_data = pd.read_csv(read_dir+'C-task_info-'+suffix+'.csv').set_index('Participant Public ID')

    add_task_c_features(df_data, ft_dict)

def process_task_d(exp_no, dir, ft_dict):
    current_date = datetime.now().strftime("%Y_%m_%d") #this assumes the files we're reading from were generated today
    suffix = "data_exp_"+exp_no+'-'+current_date
    read_dir = '../data/cleaned_data/'+dir+'/'

    df_d1_data = pd.read_csv(read_dir+'D1-task_info-'+suffix+'.csv').set_index('Participant Public ID')
    df_d1_ntlx = pd.read_csv(read_dir+'D1-NTLX_info-'+suffix+'.csv').set_index('Participant Public ID')
    df_d2_data = pd.read_csv(read_dir+'D2-task_info-'+suffix+'.csv').set_index('Participant Public ID')
    df_d3_data = pd.read_csv(read_dir+'D3-task_info-'+suffix+'.csv').set_index('Participant Public ID')

    add_task_d_features(df_d1_data, df_d1_ntlx, df_d2_data, df_d3_data, ft_dict)

#### MAIN
def main():
    ft_dict = defaultdict(defaultdict)
    p_dir = sys.argv[1] #PT or HC - i.e. Patient or Healthy Control directories
    save_dir = '../data/cleaned_data/'+p_dir+'/'
    current_date = datetime.now().strftime("%Y_%m_%d") 

    process_task_a(get_exp_no("A", p_dir), p_dir, ft_dict)
    process_task_b(get_exp_no("B", p_dir), p_dir, ft_dict)
    process_task_c(get_exp_no("C", p_dir), p_dir, ft_dict)
    process_task_d(get_exp_no("D", p_dir), p_dir, ft_dict)

    pd.DataFrame.from_dict(ft_dict, orient='index').to_csv(save_dir+'FT_INFO-'+current_date+'.csv')

main()