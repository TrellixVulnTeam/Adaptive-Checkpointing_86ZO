import os
import sys
import json
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

def get_data(src_dir, node):
    print(src_dir + "/" + node + "/cpu.json")
    if os.path.exists(src_dir + "/" + node + "/cpu.json"):
        with open(src_dir + "/" + node + "/cpu.json", 'r') as r:
            try:
                cpu_info = json.load(r)
            except Exception as e:
                print("Exception", e)
                sys.exit(1)
    return cpu_info


def draw_result(src_dir, target_dir, node):
    #get data
    save_hist_path = target_dir + "/cpu_hist_" + node + ".jpg"
    save_kde_path = target_dir + "/cpu_kde_" + node + ".jpg"
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
#     plt.show()
    plt.cla()

    #draw kde
    df = pd.DataFrame.from_dict(cpu_info)
#     print(df)
    sns.kdeplot(data=df, clip=(0, 1000))
    plt.xlabel('CPU usage %',fontsize = 10)
    plt.ylabel('Frequency', fontsize = 10)
    plt.title('Usage distribution', fontsize = 10)
    plt.savefig(save_kde_path)
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
