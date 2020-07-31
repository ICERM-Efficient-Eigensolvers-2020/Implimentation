import sys, os
THIS_FOLDER = os.path.dirname(os.path.abspath(__file__))
from efficient_eigensolvers import PowerMethod, QR_unshifted, QR_shifted, QR_wilkinson_shift, RayleighQuotientIteration
from matricesGenerator import matrix_generator
import time
import math
import matplotlib.pyplot as plt
from scipy.linalg import hessenberg
import csv

import seaborn as sns
"""
sns.set(font='Franklin Gothic Book',
        rc={
 'axes.axisbelow': False,
 'axes.edgecolor': 'lightgrey',
 'axes.grid': False,
 'axes.labelcolor': 'dimgrey',
 'axes.spines.right': False,
 'axes.spines.top': False,
 'figure.facecolor': 'white',
 'lines.solid_capstyle': 'round',
 'patch.edgecolor': 'w',
 'patch.force_edgecolor': True,
 'text.color': 'dimgrey',
 'xtick.bottom': False,
 'xtick.color': 'dimgrey',
 'xtick.direction': 'out',
 'xtick.top': False,
 'ytick.colo': 'dimgrey',
 'ytick.direction': 'out',
 'ytick.left': False,
 'ytick.right': False})

sns.set_context("notebook", rc={"font.size":16,
                                "axes.titlesize":20,
                                "axes.labelsize":18})
"""
if __name__ == '__main__':

    t = time.localtime()
    current_time = time.strftime("%H-%M-%S", t)
    top_dim = 1000
    avg = 20
    convergence_condition = 0.0001
    dim_list = [5+5*i for i in range(top_dim)]
    func_list = [QR_unshifted, QR_shifted, QR_wilkinson_shift]


    Hessen_dict = {}
    No_Hessen_dict = {}
    for func in func_list:

        Hessen_dict[func.__name__] = [0]
        No_Hessen_dict[func.__name__] = [0]

    for i, dim in enumerate(dim_list):
        print(f'testing dim {dim}')

        for _ in range(avg):
            print(f'testing average case {_}')
            #generate the random matrix
            A, eigenvals = matrix_generator(dim)
            H,Q = hessenberg(A, calc_q=True)

            for func in func_list:
                eigenvec, eigenval, iterations = func(A, convergence_condition)
                Hessen_dict[func.__name__][i] = iterations + Hessen_dict[func.__name__][i]

                #with_hessenberge:
                eigenvec, eigenval, iterations = func(H, convergence_condition)
                No_Hessen_dict[func.__name__][i] = iterations + No_Hessen_dict[func.__name__][i]

        for func in func_list:
            Hessen_dict[func.__name__][i] = Hessen_dict[func.__name__][i] / avg
            Hessen_dict[func.__name__].append(0)

            No_Hessen_dict[func.__name__][i] = No_Hessen_dict[func.__name__][i]/ avg
            No_Hessen_dict[func.__name__].append(0)

    with open(f'performance_comparison_VNC_{current_time}.csv', 'w') as csvfile:
        csvwriter = csv.writer(csvfile)
        for k, v in Hessen_dict.items():
            Hessen_dict[k] = v[:-1]
            csvwriter.writerow([k] + v[:-1])
        for k, v in No_Hessen_dict.items():
            No_Hessen_dict[k] = v[:-1]
            csvwriter.writerow([k] + v[:-1])

    tableau20 = [(31, 119, 180), (174, 199, 232), (255, 127, 14), (255, 187, 120),
                 (44, 160, 44), (152, 223, 138), (214, 39, 40), (255, 152, 150),
                 (148, 103, 189), (197, 176, 213), (140, 86, 75), (196, 156, 148),
                 (227, 119, 194), (247, 182, 210), (127, 127, 127), (199, 199, 199),
                 (188, 189, 34), (219, 219, 141), (23, 190, 207), (158, 218, 229)]

    # Scale the RGB values to the [0, 1] range, which is the format matplotlib accepts.
    for i in range(len(tableau20)):
        r, g, b = tableau20[i]
        tableau20[i] = (r / 255., g / 255., b / 255.)

    fig, ax = plt.subplots()
    ax.spines["top"].set_visible(False)
    ax.spines["bottom"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_visible(False)
    coloridx = 0
    for k, v in Hessen_dict.items():
        ax.plot(dim_list, v, label=f'{k} W Hessenberg', color=tableau20[coloridx])
        #ax.annotate( xy=(dim_list[-1],v[-1]), xytext=(5,0), textcoords='offset points', s=f'{k} w Hessenberg', va='center')
        coloridx = coloridx + 1

    coloridx = 6
    for k, v in No_Hessen_dict.items():
        ax.plot(dim_list, v, label=f'{k} W/O Hessenberg', color=tableau20[coloridx])
        coloridx = coloridx + 1
        #ax.annotate(xy=(dim_list[-1], v[-1]), xytext=(5, 0), textcoords='offset points',s=f'{k} w/o Hessenberg', va='center')

    # Remove the plot frame lines. They are unnecessary chartjunk.

    # Ensure that the axis ticks only show up on the bottom and left of the plot.
    # Ticks on the right and top of the plot are generally unnecessary chartjunk.
    ax.get_xaxis().tick_bottom()
    ax.get_yaxis().tick_left()
    plt.xlabel("Matrix Dimension")
    plt.ylabel("Iteration")
    plt.title("Performance Comparison")
    sns.despine(left=True, bottom=True)
    plt.legend(frameon=False)
    plt.savefig(f"performance_compare_iteration_VNC_{current_time}.png")
    plt.show()