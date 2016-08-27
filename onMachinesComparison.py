import sys, os, re
import logging
import numpy as np
from collections import defaultdict
import cluster_simulation_protos_pb2
import matplotlib.pyplot as plt
import itertools


#Este input dir lo sacare del argumento del sh
input_dir = "/Users/dfernandez/IdeaProjects/efficiency-cluster-scheduler-simulator/experiment_results/2016-08-26-18-13-58-vary_CL-exampleCMB_PBB_prefilled-604800"
#Estas filas tambien puedo sacarlas del sh, separadas por coma quiza, y el nombre del eje X va separado por ;
rows_string="always-power-off-decision;A"
policies = rows_string.split(",")
policies_dict_name_legend = {}
policies_single_on_machines = {}
policies_multi_on_machines = {}

for policy_entry in policies:
    name = policy_entry.split(';')[0]
    legend = policy_entry.split(';')[1]
    policies_dict_name_legend[name] = legend
rows_compare_name = ["composed-off-decision:always-power-off-decision-action:default"]
input_protobuff_monolithic_single = ""
input_protobuff_monolithic_multi = ""
for fn in os.listdir(input_dir):
     if os.path.splitext(fn)[1] == ".protobuf":
        if fn.startswith("google-monolithic-multi_path"):
            input_protobuff_monolithic_multi = os.path.join(input_dir,fn)
        elif fn.startswith("google-monolithic-single_path"):
            input_protobuff_monolithic_single = os.path.join(input_dir,fn)


if input_protobuff_monolithic_multi == "" or input_protobuff_monolithic_multi == "" :
    print "Single or Multi Path protobuf not found"
    sys.exit(1)


experiment_result_set_single = cluster_simulation_protos_pb2.ExperimentResultSet()
experiment_result_set_multi = cluster_simulation_protos_pb2.ExperimentResultSet()

single_infile = open(input_protobuff_monolithic_single, "rb")
multi_infile = open(input_protobuff_monolithic_multi, "rb")

experiment_result_set_single.ParseFromString(single_infile.read())
experiment_result_set_multi.ParseFromString(multi_infile.read())

print("Processing %d single path experiment envs."
              % len(experiment_result_set_single.experiment_env))

print("Processing %d multi path experiment envs."
              % len(experiment_result_set_multi.experiment_env))


for env in experiment_result_set_single.experiment_env:
    for exp_result in env.experiment_result:
        eff = exp_result.efficiency_stats
        for policy_name in policies_dict_name_legend.keys():
        #if any(policy_name in eff.power_off_policy.name for policy_name in policies_dict_name_legend.keys()):
            if policy_name in eff.power_off_policy.name:
                on_machines = []
                for measurement in exp_result.measurements:
                    on_machines.append(measurement.machinesOn)
                policies_single_on_machines[policy_name] =  on_machines

for env in experiment_result_set_multi.experiment_env:
    for exp_result in env.experiment_result:
        eff = exp_result.efficiency_stats
        for policy_name in policies_dict_name_legend.keys():
        #if any(policy_name in eff.power_off_policy.name for policy_name in policies_dict_name_legend.keys()):
            if policy_name in eff.power_off_policy.name:
                on_machines = []
                for measurement in exp_result.measurements:
                    on_machines.append(measurement.machinesOn)
                policies_multi_on_machines[policy_name] = on_machines


N = len(policies_dict_name_legend.keys())
figure = plt.figure(figsize=(18, 15))
plt.rcParams.update({'font.size': 25})
#ind = np.arange(N)  # the x locations for the groups
#width = 0.35
#ax1 = figure.add_subplot(1, 1, 1, position = [0.1, 0.2, 0.75, 0.75])
figure, ax1 = plt.subplots()

ax1.set_ylabel('On machines %')
ax1.set_xlabel('Time (15s)')
#ax1.set_xticklabels(policies_dict_name_legend.values())

marker = itertools.cycle((',', '+', '.', 'o', '*'))
color = itertools.cycle(('b', 'g', 'r', 'y', 'p'))
linestyle = itertools.cycle((':', '-.', '--', '-'))
for key, value in policies_single_on_machines.iteritems():
    #ax1.plot(value,linestyle='--', marker='', markersize=10, color='#ff9626', linewidth=3)
    ax1.plot(value, linestyle=linestyle.next(), marker=marker.next(), markersize=2, linewidth=1,label=policies_dict_name_legend.get(key))


#plt.rc('legend',**{'fontsize':16})
#ax1.legend((savingsSingleBar[0], savingsMultiBar[0]), ("Single", "Multi"))
ax1.set_ylim([0.60, 0.75])
ax1.legend()
plt.tight_layout()
#plt.show()
figure.savefig('monoliticsonevolutionsingle.pdf', format='PDF')



#Empieza el multi



N1 = len(policies_dict_name_legend.keys())
figure2 = plt.figure(figsize=(18, 15))
plt.rcParams.update({'font.size': 25})
#ind = np.arange(N)  # the x locations for the groups
#width = 0.35
#ax1 = figure.add_subplot(1, 1, 1, position = [0.1, 0.2, 0.75, 0.75])
figure2, ax2 = plt.subplots()

ax2.set_ylabel('On machines %')
ax2.set_xlabel('Time (15s)')
#ax1.set_xticklabels(policies_dict_name_legend.values())

marker2 = itertools.cycle((',', '+', '.', 'o', '*'))
color2 = itertools.cycle(('b', 'g', 'r', 'y', 'p'))
linestyle2 = itertools.cycle((':', '-.', '--', '-'))
for key, value in policies_multi_on_machines.iteritems():
    #ax1.plot(value,linestyle='--', marker='', markersize=10, color='#ff9626', linewidth=3)
    ax2.plot(value, linestyle=linestyle2.next(), marker=marker2.next(), markersize=2, linewidth=1,label=policies_dict_name_legend.get(key))


#plt.rc('legend',**{'fontsize':16})
#ax1.legend((savingsSingleBar[0], savingsMultiBar[0]), ("Single", "Multi"))
ax2.set_ylim([0.60, 0.75])
ax2.legend()
plt.tight_layout()
#plt.show()
figure.savefig('monoliticsonevolutionmulti.pdf', format='PDF')