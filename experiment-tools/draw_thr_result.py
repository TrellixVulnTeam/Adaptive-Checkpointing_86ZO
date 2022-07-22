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
    y = norm.pdf(bins, list_mean, list_std)  # 拟合概率分布
    plt.plot(bins, y*len(list)*len(list)*len(list), 'r--') #绘制y的曲线
    x_label = config['xlabel']
    y_label = config['ylabel']
    title = config['title']
    plt.xlabel(x_label) #绘制x轴
    plt.ylabel(y_label) #绘制y轴
    plt.title(title + exp_type + " strategy")
    plt.savefig(save_path)
    return

def draw_comparison_result(base_list, new_list, task, key, save_path):
    plt.cla()
    x = list(range(max(len(base_list), len(new_list))))
    plt.plot(x, base_list, 's-', color='r', label='default')
    plt.plot(x, new_list, 'o-', color='g', label='new')
    plt.xlabel('time')
    plt.ylabel('throughput (' + key + ')')
    plt.legend(loc='best')
    plt.savefig(save_path)
    return

def draw_every_tasks_result(metrics_info, target_dir):
    for task in metrics_info:
        if task != 'checkpoints':
            base_data = metrics_info[task]['default']
            new_data = metrics_info[task]['new']
            for key in base_data:
                base_record = convert(base_data[key])
                new_record = convert(new_data[key])
                draw_comparison_result(base_record, new_record, task, key,
                                       target_dir + "/throughput_comp_" + task + key + ".jpg")
                base_record, base_mean, base_std = remove_error_data(base_record)
                new_record, new_mean, new_std = remove_error_data(new_record)
                config = {'xlabel': 'Throughput (' + key +')',
                          'ylabel': 'Probability',
                          'title': 'Throughput distribution of task ' + task + ' based on '}
                draw_distribution_result(base_record, base_mean, base_std, 'default', key, config,
                                         target_dir + "/throughput_default_" + task + key + ".jpg")
                draw_distribution_result(new_record, new_mean, new_std, 'new', key, config,
                                         target_dir + "/throughput_new_" + task + key + ".jpg")
    return

def draw_checkpoints_result(checkpoints_info, target_dir):
    base_data = checkpoints_info['default']
    new_data = checkpoints_info['new']
    for key in ['end_to_end_duration', 'state_size']:
        base_record = convert(base_data[key])
        new_record = convert(new_data[key])
        base_record, base_mean, base_std = remove_error_data(base_record)
        new_record, new_mean, new_std = remove_error_data(new_record)
        config = {'xlabel': key,
                  'ylabel': 'Probability',
                  'title': key + ' distribution of checkpoints' + ' based on '}
        draw_distribution_result(base_record, base_mean, base_std, 'default', key, config,
                                 target_dir + "/checkpoint_default_" + key + ".jpg")
        draw_distribution_result(new_record, new_mean, new_std, 'new', key, config,
                                 target_dir + "/checkpoint_new_" + key + ".jpg")


def main(src_dir, target_dir):
    metrics_info = get_data(src_dir)
    draw_every_tasks_result(metrics_info, target_dir)
    checkpoints_info = metrics_info['checkpoints']
    draw_checkpoints_result(checkpoints_info, target_dir)

if __name__ == "__main__":
    src_dir = sys.argv[1]
    target_dir = sys.argv[2]
    main(src_dir, target_dir)
