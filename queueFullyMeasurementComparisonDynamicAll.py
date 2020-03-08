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


def plot_colourline(x,y,c):
    ax = plt.gca()
    for i in np.arange(len(x)-1):
        ax.plot([x[i],x[i+1]], [y[i],y[i+1]], 'r' if c[i] == "Mesos" else 'b')
    return

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
input_dir = "/Users/damianfernandez/IdeaProjects/score/experiment_results/RF-balance-w03-100IA"
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
input_protobuff_mesos = ""
input_protobuff_omega = ""

for fn in os.listdir(input_dir):
     if os.path.splitext(fn)[1] == ".protobuf":
        if fn.startswith("dynamic"):
            input_protobuff_dynamic = os.path.join(input_dir,fn)
        elif fn.startswith("google-mesos"):
            input_protobuff_mesos = os.path.join(input_dir,fn)
        elif fn.startswith("google-omega-resource-fit-all-or-nothing"):
            input_protobuff_omega = os.path.join(input_dir, fn)



experiment_result_set_dynamic = cluster_simulation_protos_pb2.ExperimentResultSet()
experiment_result_set_mesos = cluster_simulation_protos_pb2.ExperimentResultSet()
experiment_result_set_omega = cluster_simulation_protos_pb2.ExperimentResultSet()

dynamic_infile = open(input_protobuff_dynamic, "rb")
mesos_infile = open(input_protobuff_mesos, "rb")
omega_infile = open(input_protobuff_omega, "rb")

experiment_result_set_dynamic.ParseFromString(dynamic_infile.read())
experiment_result_set_mesos.ParseFromString(mesos_infile.read())
experiment_result_set_omega.ParseFromString(omega_infile.read())

print("Processing %d dynamic experiment envs."
              % len(experiment_result_set_dynamic.experiment_env))

first_mean = {'Dynamic':[], 'Mesos': [], 'Omega': []}
rms = []
colors = []
for env in experiment_result_set_dynamic.experiment_env:
    for exp_result in env.experiment_result:
        for measurement in exp_result.measurements:
            first_mean['Dynamic'].append(measurement.queuefullyBatch)
            rms.append(measurement.strategy)
        break

for env in experiment_result_set_mesos.experiment_env:
    for exp_result in env.experiment_result:
        for measurement in exp_result.measurements:
            first_mean['Mesos'].append(measurement.queuefullyBatch)
        break

for env in experiment_result_set_omega.experiment_env:
    for exp_result in env.experiment_result:
        for measurement in exp_result.measurements:
            first_mean['Omega'].append(measurement.queuefullyBatch)
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
ax1.set_ylabel('Queue fully (s)')
ax1.set_xlabel('# Day')
#ax1.set_xticklabels(policies_dict_name_legend.values())
runtime=86400.0 * 15
tickfrequency=60.0
numberDays=15.0
rangeDayStart = 0
rangeDayEnd = 15
dailyTicks = int(len(first_mean['Mesos'])/numberDays)
tickStart = int(rangeDayStart*dailyTicks)
tickEnd = int(rangeDayEnd*dailyTicks)
# print(tickStart, tickEnd)
# for i in np.arange(tickStart, tickEnd):
#     ax1.plot([x[i], x[i + 1]], [y[i], y[i + 1]], colors[i])
marker = itertools.cycle((',', '+', '.', 'o', '*'))
color = itertools.cycle(('b', 'g', 'r', 'y', 'p'))
linestyle = itertools.cycle(('-.', '-', '--', '-'))
for key, value in first_mean.iteritems():
    #ax1.plot(value,linestyle='--', marker='', markersize=10, color='#ff9626', linewidth=3)
    ax1.plot(value[tickStart:tickEnd], linestyle=linestyle.next(), marker=marker.next(), markersize=2, linewidth=3,label=key)
# ax1.plot(cpu_util, linestyle='-', linewidth=1)
ax1.set_ylim([0, 800.0])
numberDaysPeriod = rangeDayEnd - rangeDayStart
xtickmin = plt.xticks()[0][0]
xtickmax = plt.xticks()[0][-1]
dailyTicks = int((xtickmax - xtickmin) / numberDaysPeriod)
ticks = [ceil(dailyTicks*number) for number in range(0,numberDaysPeriod+1)]
plt.xticks(ticks, range(rangeDayStart,int(rangeDayEnd+1)))
#plt.yticks([0.05, 0.1, 0.15, 0.2, 0.25], ['50', '100', '150', '200', '250'])
#plt.yticks([0.3, 0.4, 0.5], ['30', '40', '50'])
ax1.legend()
plt.tight_layout()
figure.savefig(os.path.join(input_dir,'queuefullytevolutioncomparison.pdf'), format='PDF')