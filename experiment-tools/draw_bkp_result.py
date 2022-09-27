import os
import sys
import json
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

def get_data(src_dir):
    if os.path.exists(src_dir + "/backpressure.json"):
        with open(src_dir + "/backpressure.json", 'r') as r:
            try:
                backpressure_info = json.load(r)
            except Exception as e:
                print("Exception", e)
                sys.exit(1)
    return backpressure_info


def draw_result(src_dir, target_dir):
    #get data
    backpressure_info = get_data(src_dir)
    for task in backpressure_info:
        plt.cla()

        task_backpressure = backpressure_info[task]

        all_values = task_backpressure.values()
        min_size = sys.maxsize
        for value in all_values:
            min_size = min(len(value), min_size)
        x = list(range(min_size))

        for exp_name in task_backpressure:
            exp_data = task_backpressure[exp_name][0:min_size]
            exp_value_data = []
            for data in exp_data:
                exp_value_data.append(float(data))
            plt.plot(x, exp_value_data, label=exp_name)
        plt.legend(loc = 'best')
        plt.xlabel('time',fontsize = 10)
        plt.ylabel('Backpressure (%)', fontsize = 10)
        plt.title('Backpressure', fontsize = 10)
        if '/' in task:
            task = task.replace('/', '_')
        save_line_path = target_dir + "/backpressure_line_" + task + ".jpg"
        plt.savefig(save_line_path)
    return

def main(src_dir, target_dir):
    draw_result(src_dir, target_dir)
    return

if __name__ == "__main__":
    src_dir = sys.argv[1]
    target_dir = sys.argv[2]
    main(src_dir, target_dir)
