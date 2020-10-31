import download
import matplotlib.pyplot as plt
import numpy as np
import datetime as dm
import os, argparse

"""Plots graph for each year showing number of accidents for each region
@param data_source data structure of tuple(list[column names], list[numpy arr of values])
@param fig_location path to file where graphs will be saved
@param show_figure bool saying whether graphs should be shown to user"""
def plot_stat(data_source, fig_location=None, show_figure=False):

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

    #PLOT
    figure, axes = plt.subplots(nrows=len(years_count.keys()), ncols=1)
    #traverse subplots and their corresponding years
    for row, key in zip(axes, years_count.keys()):
        row.bar(regions, years_count[key], color='b', zorder=3)
        row.set_title(key)
        row.spines['top'].set_visible(False)
        row.spines['right'].set_visible(False)
        row.grid(axis='y', zorder=0)
        row.yaxis.set_ticks(np.arange(0, max(years_count[key]), 5000))
        #find order
        temp = sorted(years_count[key], reverse=True)
        #print values above bars
        for p in row.patches:
            row.annotate(temp.index(p.get_height())+1, 
                    (p.get_x() + p.get_width() / 2., p.get_height()), 
                    ha = 'center', va = 'center', 
                    xytext = (0, 9), 
                    textcoords = 'offset points')
    plt.tight_layout(pad=-0.5)

    #save graphs to file
    if (fig_location):
        if (not os.path.exists(os.path.dirname(fig_location))):
            os.mkdir(os.path.dirname(fig_location))
        plt.savefig(fig_location)

    #show graphs
    if (show_figure):
        plt.show()
    print("DONE")


#start from cli
if (__name__ == "__main__"):
    parser = argparse.ArgumentParser(description='plot some things')
    parser.add_argument('--show_figure', default=None, action='store_true', help="show figure")
    parser.add_argument("--fig_location", dest="fig_location", default=None)
    args = parser.parse_args()

    data_source = download.DataDownloader().get_list()
    plot_stat(data_source, args.fig_location, args.show_figure)
