import sys, os, re
import logging
import numpy as np
from collections import defaultdict
import cluster_simulation_protos_pb2
import matplotlib.pyplot as plt
import itertools


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
input_dir = "/Users/damianfernandez/IdeaProjects/cluster-scheduler-simulator/experiment_results/tr-set-v2-pr-mesos-offerBatchInterval-1s"
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
        if fn.startswith("google-omega"):
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
figure = plt.figure(figsize=(18, 15))
plt.rcParams.update({'font.size': 25})
#ind = np.arange(N)  # the x locations for the groups
#width = 0.35
#ax1 = figure.add_subplot(1, 1, 1, position = [0.1, 0.2, 0.75, 0.75])
figure, ax1 = plt.subplots()

ax1.set_ylabel('CPU util. %')
ax1.set_xlabel('Time (15s)')
#ax1.set_xticklabels(policies_dict_name_legend.values())

marker = itertools.cycle((',', '+', '.', 'o', '*'))
color = itertools.cycle(('b', 'g', 'r', 'y', 'p'))
linestyle = itertools.cycle((':', '-.', '--', '-'))
ax1.plot(cpu_util, linestyle='-', linewidth=1)


ax1.set_ylim([0.15, 0.95])
plt.tight_layout()
figure.savefig(os.path.join(input_dir,'cpuevolutiondynamic.pdf'), format='PDF')