import os
import sys
import json
import pandas
import numpy as np
from scipy.stats import norm
import matplotlib.pyplot as plt

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
    list_mean = np.mean(l)
    list_std = np.std(l)
    result = list(filter(lambda x: (x >= (list_mean-list_std)) & (x <= (list_mean + list_std)), l))
    return result, list_mean, list_std

def draw_result(list, list_mean, list_std, exp_type, save_path):
    num_bins = 20
    plt.cla()
    n, bins, patches = plt.hist(list, num_bins, color='blue', alpha=0.8) # 直方图
    y = norm.pdf(bins, list_mean, list_std)  # 拟合概率分布
    plt.plot(bins, y*len(list), 'r--') #绘制y的曲线
    plt.xlabel('Latency (ms)') #绘制x轴
    plt.ylabel('Frequency') #绘制y轴
    plt.title('Latency distribution based on ' + exp_type + ' strategy')
    plt.savefig(save_path)
    return

def main(src_dir, target_dir):
    latency_info = get_data(src_dir)
    for key in latency_info:
        latency_data = latency_info[key]
        latency_data, latency_mean, latency_std = remove_error_data(latency_data)
        draw_result(latency_data, latency_mean, latency_std, key, target_dir + "/latency_" + key + ".jpg")
    return

if __name__ == "__main__":
    src_dir = sys.argv[1]
    target_dir = sys.argv[2]
    main(src_dir, target_dir)
