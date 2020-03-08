import sys, os, re
import logging
import numpy as np
from collections import defaultdict
import cluster_simulation_protos_pb2
import matplotlib.pyplot as plt
import itertools
from math import *
from matplotlib.collections import LineCollection
from matplotlib.colors import ListedColormap, BoundaryNorm


def uniqueish_color():
    """There're better ways to generate unique colors, but this isn't awful."""
    return plt.cm.gist_ncar(np.random.random())

# def usage():
#     print "Usage: Input 1 Dir of protobuf Input 2 string of rows to perform"
#     sys.exit(1)
#
# logging.debug("len(sys.argv): " + str(len(sys.argv)))
#
# if len(sys.argv) < 2:
#     logging.error("Not enough arguments provided.")
#     usage()
#
# try:
#     input_dir = sys.argv[1]
#     rows_string = sys.argv[2]
#
# except:
#     usage()

#Este input dir lo sacare del argumento del sh
input_dir = "/Users/damianfernandez/IdeaProjects/score/experiment_results/RF-balance-w03"
#Estas filas tambien puedo sacarlas del sh, separadas por coma quiza, y el nombre del eje X va separado por ;
# rows_string="always-power-off-decision;A,random-power-off-decision;R,gamma-off;G"
# policies = rows_string.split(",")
# policies_dict_name_legend = {}
# policies_single_on_machines = {}
# policies_multi_on_machines = {}
#
# for policy_entry in policies:
#     name = policy_entry.split(';')[0]
#     legend = policy_entry.split(';')[1]
#     policies_dict_name_legend[name] = legend
# rows_compare_name = ["composed-off-decision:always-power-off-decision-action:default"]
# input_protobuff_monolithic_single = ""
# input_protobuff_monolithic_multi = ""
# for fn in os.listdir(input_dir):
#      if os.path.splitext(fn)[1] == ".protobuf":
#         if fn.startswith("google-monolithic-multi_path"):
#             input_protobuff_monolithic_multi = os.path.join(input_dir,fn)
#         elif fn.startswith("google-monolithic-single_path"):
#             input_protobuff_monolithic_single = os.path.join(input_dir,fn)
#
#
# if input_protobuff_monolithic_multi == "" or input_protobuff_monolithic_multi == "" :
#     print "Single or Multi Path protobuf not found"
#     sys.exit(1)

input_protobuff_dynamic = ""

for fn in os.listdir(input_dir):
     if os.path.splitext(fn)[1] == ".protobuf":
        if fn.startswith("dynamic"):
            input_protobuff_dynamic = os.path.join(input_dir,fn)


experiment_result_set_dynamic = cluster_simulation_protos_pb2.ExperimentResultSet()

dynamic_infile = open(input_protobuff_dynamic, "rb")

experiment_result_set_dynamic.ParseFromString(dynamic_infile.read())

print("Processing %d dynamic experiment envs."
              % len(experiment_result_set_dynamic.experiment_env))

cpu_util = []
for env in experiment_result_set_dynamic.experiment_env:
    for exp_result in env.experiment_result:
        for measurement in exp_result.measurements:
            cpu_util.append(measurement.cpuUtilization)
        break

#N = len(policies_dict_name_legend.keys())
N = 1
figure = plt.figure(figsize=(1, 3))
plt.rcParams.update({'font.size': 35})
#ind = np.arange(N)  # the x locations for the groups
#width = 0.35
#ax1 = figure.add_subplot(1, 1, 1, position = [0.1, 0.2, 0.75, 0.75])
figure, ax1 = plt.subplots(figsize=(40, 10))
ax1.margins(0)
ax1.set_ylabel('CPU utilization %')
ax1.set_xlabel('# Day')
#ax1.set_xticklabels(policies_dict_name_legend.values())

marker = itertools.cycle((',', '+', '.', 'o', '*'))
color = itertools.cycle(('b', 'g', 'r', 'y', 'p'))
linestyle = itertools.cycle((':', '-.', '--', '-'))
x = np.arange(0, len(cpu_util))
y = np.asarray(cpu_util)
points = np.array([x, y]).T.reshape(-1, 1, 2)
segments = np.concatenate([points[:-1], points[1:]], axis=1)
fig, axs = plt.subplots(2, 1, sharex=True, sharey=True)

# Create a continuous norm to map from data points to colors
norm = plt.Normalize(min(cpu_util), max(cpu_util))
lc = LineCollection(segments, cmap='viridis', norm=norm)
# Set the values used for colormapping
lc.set_array(np.asarray(cpu_util))
lc.set_linewidth(2)
line = axs[0].add_collection(lc)
fig.colorbar(line, ax=axs[0])

# Use a boundary norm instead
cmap = ListedColormap(['r', 'g', 'b'])
norm = BoundaryNorm([-1, -0.5, 0.5, 1], cmap.N)
lc = LineCollection(segments, cmap=cmap, norm=norm)
lc.set_array(np.asarray(cpu_util))
lc.set_linewidth(2)
line = axs[1].add_collection(lc)
fig.colorbar(line, ax=axs[1])

axs[0].set_xlim(x.min(), x.max())
axs[0].set_ylim(-1.1, 1.1)
plt.show()




# ax1.plot(cpu_util, linestyle='-', linewidth=1)
# ax1.set_ylim([0.26, 0.7])
# locs, labels = plt.xticks()
# runtime=86400.0 * 15
# tickfrequency=50.0
# numberDays=15.0
# ticks = [ceil(((runtime/tickfrequency)/numberDays)*number) for number in range(0,int(numberDays+1))]
# #plt.xticks([0, ])
# #plt.xticks([0, ceil(((runtime/tickfrequency)/numberDays)*1.0), (((runtime/tickfrequency)/numberDays)*2.0), ceil(((runtime/tickfrequency)/numberDays)*3.0), ceil(((runtime/tickfrequency)/numberDays)*4.0), ceil(((runtime/tickfrequency)/numberDays)*5.0), ceil(((runtime/tickfrequency)/numberDays)*6.0), ceil(((runtime/tickfrequency)/numberDays)*7.0)], ['0', '1', '2', '3', '4', '5', '6', '7'])
# plt.xticks(ticks, range(0,int(numberDays+1)))
# plt.yticks([0.3, 0.4, 0.5, 0.6, 0.7], ['30', '40', '50', '60', '70'])
#
# plt.tight_layout()
# figure.savefig(os.path.join(input_dir,'cpuevolutiondynamic.pdf'), format='PDF')