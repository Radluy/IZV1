import download
import matplotlib.pyplot as plt
import numpy as np
import datetime as dm
import os, argparse
#tuple(list[str], list[np.ndarray])

def plot_stat(data_source, fig_location=None, show_figure=False):

    #fig = plt.figure(figsize=(6, 4))

    #get indices of region changes in array
    reg_arr = data_source[1][data_source[1].__len__() - 1]
    indices = [0]
    tmp = None
    i = 0
    while (i < reg_arr.size - 1):
        tmp = reg_arr[i]
        while (reg_arr[i] == tmp):
            if (i == reg_arr.size - 1):
                break
            else:
                i += 1
        indices.append(i)
    regions = []
    for index in indices[1:]:
        regions.append(reg_arr[index - 1])
    years_count = {
        "2016": [],
        "2017": [],
        "2018": [],
        "2019": [],
        "2020": []
    }
    #count accidents by year
    for i in range(indices.__len__()-1):
            years = np.datetime_as_string(data_source[1][3][indices[i]:indices[i+1]], unit='Y')
            years_count["2016"].append(np.count_nonzero(years == "2016"))
            years_count["2017"].append(np.count_nonzero(years == "2017"))
            years_count["2018"].append(np.count_nonzero(years == "2018"))
            years_count["2019"].append(np.count_nonzero(years == "2019"))
            years_count["2020"].append(np.count_nonzero(years == "2020"))

    #plot
    figure, axes = plt.subplots(nrows=len(years_count.keys()), ncols=1)
    for row, key in zip(axes, years_count.keys()):
        row.bar(regions, years_count[key], color='C3')
        row.set_title(key)
        #row.set_xlabel("Regions")
        #row.set_ylabel("Accidents")
        row.spines['top'].set_visible(False)
        row.spines['right'].set_visible(False)
        row.spines['bottom'].set_position('zero')
        row.margins(0.05)
        row.set
    #plt.setp(row.get_xticklabels()[5:8], color="white")
    #plt.setp(row.get_xticklines()[10:15], markeredgecolor="white")
    plt.tight_layout()

    if (fig_location):
        if (not os.path.exists(os.path.dirname(fig_location))):
            os.mkdir(os.path.dirname(fig_location))
        plt.savefig(fig_location)

    if (show_figure):
        plt.show()
    print("DONE")



if (__name__ == "__main__"):
    parser = argparse.ArgumentParser(description='plot some things')
    parser.add_argument('--show_figure', default=None, action='store_true', help="show figure")
    parser.add_argument("--fig_location", dest="fig_location", default=None)
    args = parser.parse_args()

    data_source = download.DataDownloader().get_list(["STC", "HKK", "JHM"])
    plot_stat(data_source, args.fig_location, args.show_figure)
