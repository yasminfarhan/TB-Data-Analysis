import pickle 

# Run this file only if q_info_dict needs modifying - e.g. if a new questionnaire has been added

q_info_dict = {

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
  "NTLX_1" : {
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
  "NTLX_2" : {
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
  "NTLX_3" : {
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
  "NTLX_4" : {
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
  "NTLX_5" : {
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
  "NTLX_6" : {
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

def main():
    # Read in questionnaire mapping dictionary
    with open('q_map.pkl', 'wb') as file:
        pickle.dump(q_info_dict, file)  

main()