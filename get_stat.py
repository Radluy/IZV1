import download 
import matplotlib.pyplot as plt
import numpy as np
import datetime as dm
#tuple(list[str], list[np.ndarray])

def plot_stat(data_source, fig_location=None, show_figure=False):

    regions = np.unique(data_source[1][data_source[1].__len__() - 1])

    #fig = plt.figure()
    #ax = fig.add_axes([0.2, 0.2, 0.8, 0.8])

    #test = np.where(data_source[1][3] == np.datetime64("2017"))

    counts = list()
    for region in regions:
        counts.append(np.count_nonzero(data_source[1][data_source[1].__len__()-1] == region))

    #fig, axes = plt.subplots(ncols=2, nrows=2, constrained_layout=True, figsize=(6, 4))
    #(ax1,ax2),(ax3,ax4) =axes
    #axes.bar(regions, counts)

    fig = plt.figure(figsize=(6, 4))
    ax = fig.add_subplot()
    ax.bar(regions, counts, color='C3')#align='center', width=0.5, bottom=0
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['bottom'].set_position('zero')
    ax.margins(0.05)
    #plt.setp(ax.get_xticklabels()[5:8], color="white")
    #plt.setp(ax.get_xticklines()[10:15], markeredgecolor="white")
    plt.tight_layout()
    plt.show()
    print("DONE")





data_source = download.DataDownloader().get_list(["STC", "HKK", "JHM"])
plot_stat(data_source)
