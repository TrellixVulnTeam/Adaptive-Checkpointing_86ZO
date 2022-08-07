import os
import sys
import json
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from statsmodels.distributions.empirical_distribution import ECDF

def get_data(src_dir, node):
    if os.path.exists(src_dir + "/" + node + "/cpu.json"):
        with open(src_dir + "/" + node + "/cpu.json", 'r') as r:
            try:
                cpu_info = json.load(r)
            except Exception as e:
                print("Exception", e)
                sys.exit(1)
    return cpu_info

def remove_error_data(l):
    data_array = np.asarray(l)
    list_mean = np.mean(l)
    list_std = np.std(l)
#     l = [x for x in l if (x > list_mean - 3*list_std)]
#     l = [x for x in l if (x < list_mean + 3*list_std)]
    l = [x for x in l if (x != 0)]
    return l

def draw_result(src_dir, target_dir, node):
    #get data
    save_hist_path = target_dir + "/cpu_hist_" + node + ".jpg"
    save_cdf_path = target_dir + "/cpu_cdf_" + node + "_"
    cpu_info = get_data(src_dir, node)

    #draw histograme
    bins = 20
    plt.style.use('seaborn-deep')
    plt.cla()
    plt.hist(cpu_info.values(), bins, label=[l for l in cpu_info.keys()])
    plt.legend(loc = "upper right")
    plt.xlabel('CPU usage',fontsize = 10)
    plt.ylabel('Frequency', fontsize = 10)
    plt.title('Usage distribution', fontsize = 10)
    plt.savefig(save_hist_path)

    # draw cdf

# ===  if you want to plot cdfs of different strategies in one plot
#     plt.cla()
#     for exp_name in cpu_info:
#         exp_data = cpu_info[exp_name]
#         ecdf = ECDF(exp_data)
#         x = np.linspace(min(exp_data), max(exp_data))
#         y = ecdf(x)
#         plt.step(x, y, label=exp_name)
#
#     plt.xlabel('CPU usage (%)',fontsize = 10)
#     plt.ylabel('CDF', fontsize = 10)
#     plt.title('CPU usage CDF', fontsize = 10)
#     plt.savefig(save_cdf_path+".jpg")

# ==========================================
# === if you want to plot cdfs of different strategies in different plots
    for exp_name in cpu_info:
        plt.cla()
        exp_data = cpu_info[exp_name]
        exp_data = remove_error_data(exp_data)
        ecdf = ECDF(exp_data)
        x = np.linspace(min(exp_data), max(exp_data))
        y = ecdf(x)
        plt.step(x, y, label=exp_name)
        plt.legend(loc = 'best')
        plt.xlabel('CPU usage (%)', fontsize = 10)
        plt.ylabel('CDF', fontsize = 10)
        plt.title('CPU usage CDF', fontsize = 10)
        plt.savefig(save_cdf_path + exp_name + ".jpg")
    return

def main(src_dir, target_dir):
    node_list = os.listdir(src_dir)
    for node in node_list:
        if os.path.isdir(src_dir + "/" + node):
            draw_result(src_dir, target_dir, node)
    return

if __name__ == "__main__":
    src_dir = sys.argv[1]
    target_dir = sys.argv[2]
    main(src_dir, target_dir)
