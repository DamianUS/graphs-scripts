import sys, os, re
import logging
import numpy as np
from collections import defaultdict
import cluster_simulation_protos_pb2
import matplotlib.pyplot as plt


#Este input dir lo sacare del argumento del sh
#input_dir = "/Users/dfernandez/IdeaProjects/efficiency-cluster-scheduler-simulator/experiment_results/2016-08-26-18-13-58-vary_CL-exampleCMB_PBB_prefilled-604800"
#Estas filas tambien puedo sacarlas del sh, separadas por coma quiza, y el nombre del eje X va separado por ;
#rows_string="always-power-off-decision;A,no-power-off-decision;N"#
#rows_string="always-power-off-decision;A"

def usage():
    print "Usage: Input 1 Dir of protobuf Input 2 string of rows to perform"
    sys.exit(1)

logging.debug("len(sys.argv): " + str(len(sys.argv)))

if len(sys.argv) < 2:
    logging.error("Not enough arguments provided.")
    usage()

try:
    input_dir = sys.argv[1]
    rows_string = sys.argv[2]

except:
    usage()
policies = rows_string.split(",")
policies_dict_name_legend = {}
policies_single_savings = {}
policies_multi_savings = {}
policies_single_batch_think = {}
policies_multi_batch_think = {}
policies_single_service_think = {}
policies_multi_service_think = {}

for policy_entry in policies:
    name = policy_entry.split(';')[0]
    legend = policy_entry.split(';')[1]
    policies_dict_name_legend[name] = legend
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
                for workload_stat in exp_result.workload_stats:
                    policies_single_savings[policy_name] = (1 - (
                    eff.total_energy_consumed / eff.current_energy_consumed)) * 100
                    if workload_stat.workload_name == "Service":
                        policies_single_service_think[policy_name] = workload_stat.job_think_times_90_percentile
                    elif workload_stat.workload_name == "Batch":
                        policies_single_batch_think[policy_name] = workload_stat.job_think_times_90_percentile

for env in experiment_result_set_multi.experiment_env:
    for exp_result in env.experiment_result:
        eff = exp_result.efficiency_stats
        for policy_name in policies_dict_name_legend.keys():
        #if any(policy_name in eff.power_off_policy.name for policy_name in policies_dict_name_legend.keys()):
            if policy_name in eff.power_off_policy.name:
                for workload_stat in exp_result.workload_stats:
                    policies_multi_savings[policy_name] = (1 - (
                    eff.total_energy_consumed / eff.current_energy_consumed)) * 100
                    if workload_stat.workload_name == "Service":
                        policies_multi_service_think[policy_name] = workload_stat.job_think_times_90_percentile
                    elif workload_stat.workload_name == "Batch":
                        policies_multi_batch_think[policy_name] = workload_stat.job_think_times_90_percentile



N = len(policies_dict_name_legend.keys())
figure = plt.figure(figsize=(9, 7.5))
plt.rcParams.update({'font.size': 25})
ind = np.arange(N)  # the x locations for the groups
width = 0.35
#ax1 = figure.add_subplot(1, 1, 1, position = [0.1, 0.2, 0.75, 0.75])
figure, ax1 = plt.subplots()
savingsSingleBar = ax1.bar(ind, policies_single_savings.values(), width, color='#007dad')
savingsMultiBar = ax1.bar(ind+width, policies_multi_savings.values(), width, color='#ec6200')

ax1.set_ylabel('Total Savings %')
ax1.set_ylim([10, 25])
ax1.set_xlabel('Energy Policy')
ax1.set_xticks(ind + width)
policies_dict_name_legend.values()
ax1.set_xticklabels(policies_dict_name_legend.values())

ax2 = ax1.twinx()
batchPlot = ax2.plot(ind+width, policies_single_batch_think.values(), marker='^', markersize=10, linestyle='--', color='#04d8ff', linewidth=3)
servicePlot = ax2.plot(ind+width, policies_single_service_think.values(),  marker='.', markersize=10, linestyle='-', color='#18b0ea', linewidth=3)

ax2.plot(ind+width,policies_multi_batch_think.values(),linestyle='--', marker='^', markersize=10, color='#ff9626', linewidth=3)
ax2.plot(ind+width,policies_multi_service_think.values(),linestyle='-', marker='.', markersize=10, color='#ffa038', linewidth=3)
ax2.set_ylabel('Job think time (s)')

plt.rc('legend',**{'fontsize':16})
ax1.legend((batchPlot[0], servicePlot[0]), ("Batch", "Service"))
plt.tight_layout()
#plt.show()
figure.savefig(os.path.join(input_dir,'monoliticsavingsvjobthink.pdf'), format='PDF')