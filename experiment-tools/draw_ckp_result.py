import os
import sys
import json
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from statsmodels.distributions.empirical_distribution import ECDF

def get_data(src_dir):
    if os.path.exists(src_dir + "/checkpoints.json"):
        with open(src_dir + "/checkpoints.json", 'r') as r:
            try:
                checkpoints_info = json.load(r)
            except Exception as e:
                print("Exception", e)
                sys.exit(1)
    return checkpoints_info

def remove_error_data(l):
    data_array = np.asarray(l)
    list_mean = np.mean(l)
    list_std = np.std(l)
    l = [x for x in l if (x > list_mean - 3*list_std)]
    l = [x for x in l if (x < list_mean + 3*list_std)]
    return l

def draw_result(src_dir, target_dir):
    #get data
    checkpoints_info = get_data(src_dir)
    for key in checkpoints_info:
        if "average" not in key:
            save_hist_path = target_dir + "/checkpoints_hist_" + key + ".jpg"
            save_cdf_path = target_dir + "/checkpoints_cdf_" + key + "_"
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

            # draw cdf

# ===  if you want to plot cdfs of different strategies in one plot
#             plt.cla()
#             for exp_name in key_info:
#                 exp_data = key_info[exp_name]
#                 ecdf = ECDF(exp_data)
#                 x = np.linspace(min(exp_data), max(exp_data))
#                 y = ecdf(x)
#                 plt.step(x, y, label=exp_name)
#
#             plt.xlabel(key,fontsize = 10)
#             plt.ylabel('CDF', fontsize = 10)
#             plt.title(key +' CDF', fontsize = 10)
#             plt.savefig(save_cdf_path+".jpg")
# ==========================================
# === if you want to plot cdfs of different strategies in different plots

            for exp_name in key_info:
                plt.cla()
                exp_data = key_info[exp_name]
                exp_data = remove_error_data(exp_data)
                ecdf = ECDF(exp_data)
                x = np.linspace(min(exp_data), max(exp_data))
                y = ecdf(x)
                plt.step(x, y, label=exp_name)
                plt.legend(loc = 'best')
                plt.xlabel(key, fontsize = 10)
                plt.ylabel('CDF', fontsize = 10)
                plt.title(key + ' CDF', fontsize = 10)
                plt.savefig(save_cdf_path + exp_name + ".jpg")

    return

def main(src_dir, target_dir):
    draw_result(src_dir, target_dir)
    return

if __name__ == "__main__":
    src_dir = sys.argv[1]
    target_dir = sys.argv[2]
    main(src_dir, target_dir)
