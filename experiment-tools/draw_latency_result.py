import os
import sys
import json
import pandas
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

def get_data(src_dir):
    if os.path.exists(src_dir + "/latency.json"):
        with open(src_dir + "/latency.json", 'r') as r:
            try:
                latency_info = json.load(r)
            except Exception as e:
                print("Exception", e)
                sys.exit(1)
        base_data = latency_info['base']
        new_data = latency_info['new']
    return base_data, new_data

def remove_error_data(list):
    list_mean = np.mean(list)
    list_std = np.std(list)
    list = filter(lambda x: x >= list_mean - 3*list_std & x <= list_mean + 3*list, list)
    return list, list_mean, list_std

def draw_result(src_dir, target_dir):
    #get data
    save_hist_path = target_dir + "/latency.jpg"
    save_kde_path = target_dir + "/kde.jpg"
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
    plt.show()

    #draw kde
    df = pd.DataFrame.from_dict(latency_info)
    print(df)
    sns.kdeplot(data=df, clip=(0, 1000))
    plt.xlabel('Latency (ms)',fontsize = 10)
    plt.ylabel('Frequency', fontsize = 10)
    plt.title('Latency distribution', fontsize = 10)
    plt.savefig(save_kde_path)
    return

def main(src_dir, target_dir):
    draw_result(src_dir, target_dir)
    return

if __name__ == "__main__":
    src_dir = sys.argv[1]
    target_dir = sys.argv[2]
    main(src_dir, target_dir)
