import os
import sys
import json
import pandas
import numpy as np
import matplotlib.mlab as mlab
import matplotlib.pyplot as plt

def get_data(src_dir, node, exp_type, token, file_name):
    ret_list = []
    for line in open(src_dir+"/"+node+"/"+exp_type+"/" + file_name):
        if token not in line:
            continue
        value = find_number(line)
        if (value != -1):
            ret_list.append(value)
    return ret_list

def find_number(line):
    for i, c in line:
        if c.isdigit():
            return float(line[i:])
    return -1

def get_cpu_usage(src_dir, node):
    user_base = get_data(src_dir, node, 'default', 'user', 'cpu_record.txt')
    user_new = get_data(src_dir, node, 'new', 'user', 'cpu_record.txt')
    total_base = get_data(src_dir, node, 'default', 'cpu', 'cpu_record.txt')
    total_new = get_data(src_dir, node, 'new', 'cpu', 'cpu_record.txt')
    return user_base, user_new, total_base, total_new

def get_cpu_threads(src_dir, node):
    threads_base = get_data(src_dir, node, 'default', 'Threads', 'thread_num_record.txt')
    threads_new = get_data(src_dir, node, 'new', 'Threads', 'thread_num_record.txt')
    return threads_base, threads_new

def draw_result(list, exp_type, token, save_path):
    num_bins = 20
    list_mean = np.mean(list)
    list_std = np.std(list)
    plt.cla()
    n, bins, patches = plt.hist(list, num_bins, normed=1, facecolor='blue', alpha=0.8) # 直方图
    y = mlab.normpdf(bins, list_mean, list_std)  # 拟合概率分布
    plt.plot(bins, y, 'r--') #绘制y的曲线
    plt.xlabel(token) #绘制x轴
    plt.ylabel('Probability') #绘制y轴
    plt.title(token + ' distribution based on ' + exp_type + ' strategy')
    plt.savefig(save_path)
    return

def draw_cpu_usage(src_dir. target_dir, node):
    user_base, user_new, total_base, total_new = get_cpu_usage(src_dir, node)
    draw_result(user_base, 'default', 'user cpu usage', target_dir + "/" + node + "_cpu_usage_user_default.jpg")
    draw_result(user_new, 'new', 'user cpu usage', target_dir + "/" + node + "_cpu_usage_user_new.jpg")
    draw_result(total_base, 'default', 'total cpu usage', target_dir + "/" + node + "_cpu_usage_total_default.jpg")
    draw_result(total_new, 'new', 'total cpu usage', target_dir + "/" + node + "_cpu_usage_total_new.jpg")
    return

def draw_cpu_threads(src_dir, target_dir, node)
    threads_base, threads_new = get_cpu_threads(src_dir, node)
    draw_result(threads_base, 'default', 'threads number', target_dir + "/" + node + "_threads_number_default.jpg")
    draw_result(threads_new, 'new', 'threads number', target_dir + "/" + node + "_threads_number_new.jpg")
    return

def main(src_dir, target_dir):
    node_list = os.listdir(src_dir)
    for node in node_list:
        draw_cpu_usage(src_dir, target_dir, node)
        draw_cpu_threads(src_dir, target_dir, node)
    return

if __name__ == "__main__":
    src_dir = sys.argv[1]
    target_dir = sys.argv[2]
    main(src_dir, target_dir)

