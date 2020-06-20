import math
import numpy as np

def get_ax_size(ax, fig):
    bbox = ax.get_window_extent().transformed(fig.dpi_scale_trans.inverted())

    width, height = bbox.width, bbox.height
    #width *= fig.dpi
    #height *= fig.dpi
    return width, height

def find_opt_arangement(k, ratio = 1):
    i = np.argmin([math.fabs(math.ceil(k/j)-ratio* j) for j in range(1,k+1)])+1
    j = math.ceil(k/i)
    return int(i),j