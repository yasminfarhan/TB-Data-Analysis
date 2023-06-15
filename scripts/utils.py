
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