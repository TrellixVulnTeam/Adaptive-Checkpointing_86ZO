import os
import sys
import json
import pandas
import numpy as np
from scipy.stats import norm
import matplotlib.pyplot as plt

def get_data(src_dir):
    info = {}
    if os.path.exists(src_dir + "/metrics.json"):
        with open(src_dir + "/metrics.json", 'r') as r:
            try:
                info = json.load(r)
            except Exception as e:
                print("Exception", e)
                sys.exit(1)
    return info

def convert(list):
    num_list = []
    for item in list:
        num_list.append(float(item))
    return num_list

def remove_error_data(l):
    list_mean = np.mean(l)
    list_std = np.std(l)
    result = list(filter(lambda x: (x >= (list_mean-list_std)) & (x <= (list_mean+list_std)), l))
    return result, list_mean, list_std

def draw_distribution_result(list, list_mean, list_std, exp_type, key, config, save_path):
    num_bins = 20
    plt.cla()
    n, bins, patches = plt.hist(list, num_bins, color='blue', alpha=0.8) # 直方图
#     y = norm.pdf(bins, list_mean, list_std)  # 拟合概率分布
#     plt.plot(bins, y*len(list)*len(list)*len(list), 'r--') #绘制y的曲线
    x_label = config['xlabel']
    y_label = config['ylabel']
    title = config['title']
    plt.xlabel(x_label) #绘制x轴
    plt.ylabel(y_label) #绘制y轴
    plt.title(title + exp_type + " strategy")
    plt.savefig(save_path)
    return

def draw_comparison_result(lists, task, key, save_path):
    plt.cla()
    if len(lists) == 1:
        for exp_type in lists:
            list_data = lists[exp_type]
            x = list(range(list_data))
            plt.plot(x, list_data, 's-', color='r', label=exp_type)
    elif len(lists) == 2:
        all_values = list(lists.values())
        r = min(len(all_values[0]), len(all_values[1]))
        x = list(range(r))
#         print("=======\n")
#         print(task, key)
#         print(len(lists['default']))
#         print("\n")
        plt.plot(x, lists['default'][0:r], 's-', color='r', label='default')
        plt.plot(x, lists['new'][0:r], 'o-', color='g', label='new')

    plt.xlabel('time')
    plt.ylabel('throughput (' + key + ')')
    plt.legend(loc='best')
    plt.savefig(save_path)
    return

def draw_every_tasks_result(metrics_info, target_dir):
    for task in metrics_info:
        if task != 'checkpoints':
            thr_data = metrics_info[task]
#             base_data = metrics_info[task]['default']
#             new_data = metrics_info[task]['new']
            comp_lists = {}
            for exp_type in thr_data:
                for key in thr_data[exp_type]:
                    record_data = convert(thr_data[exp_type][key])
                    record_data, record_mean, record_std = remove_error_data(record_data)
                    config = {'xlabel': 'Throughput (' + key +')',
                              'ylabel': 'Frequency',
                              'title': 'Throughput distribution of task ' + task + ' based on '}
                    draw_distribution_result(record_data, record_mean, record_std, exp_type, key, config,
                                             target_dir + "/throughput_" + exp_type + "_" + task + "_" + key + ".jpg")
                    if key in comp_lists:
                        comp_lists[key][exp_type] = record_data
                    else:
                        new_dict = {}
                        new_dict[exp_type] = record_data
                        comp_lists[key] = new_dict
            for key in comp_lists:
                records = comp_lists[key]
                draw_comparison_result(records, task, key,
                                       target_dir + "/throughput_comp_" + task + "_" + key + ".jpg")
    return

def draw_checkpoints_result(checkpoints_info, target_dir):
    for exp_type in checkpoints_info:
        data = checkpoints_info[exp_type]
        for key in ['end_to_end_duration', 'state_size']:
            record_data = convert(data[key])
            record_data, record_mean, record_std = remove_error_data(record_data)
            config = {'xlabel': key,
                      'ylabel': 'Frequency',
                      'title': key + ' distribution of checkpoints' + ' based on '}
            draw_distribution_result(record_data, record_mean, record_std, exp_type, key, config,
                                     target_dir + "/checkpoint_ " + exp_type + "_" + key + ".jpg")


def main(src_dir, target_dir):
    metrics_info = get_data(src_dir)
    draw_every_tasks_result(metrics_info, target_dir)
    checkpoints_info = metrics_info['checkpoints']
    draw_checkpoints_result(checkpoints_info, target_dir)

if __name__ == "__main__":
    src_dir = sys.argv[1]
    target_dir = sys.argv[2]
    main(src_dir, target_dir)
