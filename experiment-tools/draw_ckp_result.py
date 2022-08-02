import os
import sys
import json
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

def get_data(src_dir):
    if os.path.exists(src_dir + "/checkpoints.json"):
        with open(src_dir + "/checkpoints.json", 'r') as r:
            try:
                checkpoints_info = json.load(r)
            except Exception as e:
                print("Exception", e)
                sys.exit(1)
    return checkpoints_info

def remove_error_data(list):
    list_mean = np.mean(list)
    list_std = np.std(list)
    list = filter(lambda x: x >= list_mean - 3*list_std & x <= list_mean + 3*list, list)
    return list, list_mean, list_std

def draw_result(src_dir, target_dir):
    #get data
    checkpoints_info = get_data(src_dir)
    for key in checkpoints_info:
        if "average" not in key:
            save_hist_path = target_dir + "/checkpoints_hist_" + key + ".jpg"
            save_kde_path = target_dir + "/checkpoints_kde_" + key + ".jpg"
            key_info = checkpoints_info[key]

            #draw histograme
            bins = 40
            plt.style.use('seaborn-deep')
            plt.cla()
            plt.hist(key_info.values(), bins, label=[l for l in key_info.keys()])
            plt.legend(loc = "upper right")
            plt.xlabel(key, fontsize = 10)
            plt.ylabel('Frequency', fontsize = 10)
            plt.title('Distribution', fontsize = 10)
            plt.savefig(save_hist_path)
        #     plt.show()
            plt.cla()

            #draw kde
            df = pd.DataFrame.from_dict(key_info)
        #     print(df)
            sns.kdeplot(data=df, clip=(0, 1000))
            plt.xlabel(key,fontsize = 10)
            plt.ylabel('Frequency', fontsize = 10)
            plt.title('Distribution', fontsize = 10)
            plt.savefig(save_kde_path)
    return

def main(src_dir, target_dir):
    draw_result(src_dir, target_dir)
    return

if __name__ == "__main__":
    src_dir = sys.argv[1]
    target_dir = sys.argv[2]
    main(src_dir, target_dir)
