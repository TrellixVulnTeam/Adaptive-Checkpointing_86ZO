import os
import sys
import json
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from statsmodels.distributions.empirical_distribution import ECDF

def get_data(src_dir):
    if os.path.exists(src_dir + "/latency.json"):
        with open(src_dir + "/latency.json", 'r') as r:
            try:
                latency_info = json.load(r)
            except Exception as e:
                print("Exception", e)
                sys.exit(1)
    return latency_info

def remove_error_data(l):
    data_array = np.asarray(l)
    list_mean = np.mean(l)
    list_std = np.std(l)
    l = [x for x in l if (x > list_mean - 3*list_std)]
    l = [x for x in l if (x < list_mean + 3*list_std)]
    return l

def draw_result(src_dir, target_dir):
    #get data
    save_hist_path = target_dir + "/latency_hist.jpg"
    save_cdf_path = target_dir + "/latency_cdf_"
    latency_info = get_data(src_dir)

    #draw histograme
    bins = 20
    plt.style.use('seaborn-deep')
    plt.cla()
    plt.hist(latency_info.values(), bins, label=[l for l in latency_info.keys()])
    plt.legend(loc = "upper right")
    plt.xlabel('Latency (ms)',fontsize = 10)
    plt.ylabel('Frequency', fontsize = 10)
    plt.title('Latency distribution', fontsize = 10)
    plt.savefig(save_hist_path)

    #draw cdf
#
# ===  if you want to plot cdfs of different strategies in one plot
    plt.cla()
    for exp_name in latency_info:
        exp_data = latency_info[exp_name]
        ecdf = ECDF(exp_data)
        x = np.linspace(min(exp_data), max(exp_data))
        y = ecdf(x)
        plt.step(x, y, label=exp_name)

    plt.legend(loc = 'best')
    plt.xlabel('Latency (ms)',fontsize = 10)
    plt.ylabel('CDF', fontsize = 10)
    plt.title('Latency CDF', fontsize = 10)
    plt.savefig(save_cdf_path+".jpg")

# ===============================================
# if you want to plot cdfs of different strategies in different plots
    for exp_name in latency_info:
        plt.cla()
        exp_data = latency_info[exp_name]
        exp_data = remove_error_data(exp_data)
        ecdf = ECDF(exp_data)
        x = np.linspace(min(exp_data), max(exp_data))
        y = ecdf(x)
        plt.step(x, y, label=exp_name)
        plt.legend(loc = 'best')
        plt.xlabel('Latency (ms)', fontsize = 10)
        plt.ylabel('CDF', fontsize = 10)
        plt.title('Latency CDF', fontsize = 10)
        plt.savefig(save_cdf_path + exp_name + ".jpg")
    return

def main(src_dir, target_dir):
    draw_result(src_dir, target_dir)
    return

if __name__ == "__main__":
    src_dir = sys.argv[1]
    target_dir = sys.argv[2]
    main(src_dir, target_dir)
