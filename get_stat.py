import download 
import matplotlib.pyplot as plt
import numpy as np
import datetime as dm
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

    for i in range(indices.__len__()-1):
            years = np.datetime_as_string(data_source[1][3][indices[i]:indices[i+1]], unit='Y')
            years_count["2016"].append(np.count_nonzero(years == "2016"))
            years_count["2017"].append(np.count_nonzero(years == "2017"))
            years_count["2018"].append(np.count_nonzero(years == "2018"))
            years_count["2019"].append(np.count_nonzero(years == "2019"))
            years_count["2020"].append(np.count_nonzero(years == "2020"))

    figure, axes = plt.subplots(nrows=len(years_count.keys()), ncols=1)
    i, j = 0, 0
    """ax = fig.add_subplot(211)
    ax.set_title(key)
    ax.set_xlabel("Regions")
    ax.bar(regions, years_count[key], color='C3')  #align='center', width=0.5, bottom=0
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['bottom'].set_position('zero')
    ax.margins(0.05)"""
    for row, key in zip(axes, years_count.keys()):
        row.bar(regions, years_count[key], color='C3')
        row.set_title(key)
        row.set_xlabel("Regions")
        row.set_ylabel("Accidents")
        row.spines['top'].set_visible(False)
        row.spines['right'].set_visible(False)
        row.spines['bottom'].set_position('zero')
        row.margins(0.05)
        row.set
    #plt.setp(row.get_xticklabels()[5:8], color="white")
    #plt.setp(row.get_xticklines()[10:15], markeredgecolor="white")
    plt.tight_layout()
    plt.show()
    print("DONE")





data_source = download.DataDownloader().get_list(["STC", "HKK", "JHM"])
plot_stat(data_source)
