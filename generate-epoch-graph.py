import sys, os
import logging
import numpy as np
import collections
import cluster_simulation_protos_pb2
import matplotlib.pyplot as plt
import itertools
from math import *


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
policies_single_kw = {}
policies_multi_kw = {}
policies_single_idle = {}
policies_multi_idle = {}
policies_single_service_90p_first = {}
policies_multi_service_90p_first = {}
policies_single_service_90p_fully = {}
policies_multi_service_90p_fully = {}
policies_single_on_machines = {}
policies_multi_on_machines = {}
policies_single_epochs = {}
policies_multi_epochs = {}

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
print("Empieza a leer single")
single_infile = open(input_protobuff_monolithic_single, "rb")
experiment_result_set_single.ParseFromString(single_infile.read())
single_infile.close()
print("Termina de leer single")
picker_name = "agnieszka-energy-security-picker-random"

for env in experiment_result_set_single.experiment_env:
    for exp_result in env.experiment_result:
        eff = exp_result.efficiency_stats
        for policy_name in policies_dict_name_legend.keys():
        #if any(policy_name in eff.power_off_policy.name for policy_name in policies_dict_name_legend.keys()):
            if policy_name in eff.power_off_policy.name and picker_name in eff.picking_policy:
                policies_single_savings[policy_name] = (1 - (eff.total_energy_consumed / eff.current_energy_consumed)) * 100
                #measurements
                on_machines = []
                for index, measurement in enumerate(exp_result.measurements):
                    if index < len(exp_result.measurements) - 500:
                        on_machines.append(measurement.machinesOn)
                policies_single_on_machines[policy_name] = on_machines
                #kwh
                policies_single_kw[policy_name] = eff.kwh_saved_per_shutting
                #idle
                policies_single_idle[policy_name] = (eff.avg_number_machines_on / 10000 - max(
                    exp_result.cell_state_avg_cpu_utilization, exp_result.cell_state_avg_mem_utilization)) * 100
                for workload_stat in exp_result.workload_stats:
                    if workload_stat.workload_name == "Service":
                        # queue times
                        policies_single_service_90p_first[policy_name] = workload_stat.job_queue_time_till_first_scheduled_90_percentile
                        policies_single_service_90p_fully[policy_name] = workload_stat.job_queue_time_till_fully_scheduled_90_percentile
                        #job think time
                        policies_single_service_think[policy_name] = workload_stat.job_think_times_90_percentile
                    elif workload_stat.workload_name == "Batch":
                        policies_single_batch_think[policy_name] = workload_stat.job_think_times_90_percentile
                        epochs = []
                        for epoch in workload_stat.epochs:
                            epochs.append(epoch.fintess_avg)
                            policies_single_epochs[policy_name] = epochs


print("Empieza a leer multi")
multi_infile = open(input_protobuff_monolithic_multi, "rb")
experiment_result_set_multi.ParseFromString(multi_infile.read())
multi_infile.close()
print("Termina de leer multi")

for env in experiment_result_set_multi.experiment_env:
    for exp_result in env.experiment_result:
        eff = exp_result.efficiency_stats
        for policy_name in policies_dict_name_legend.keys():
        #if any(policy_name in eff.power_off_policy.name for policy_name in policies_dict_name_legend.keys()):
            if policy_name in eff.power_off_policy.name and picker_name in eff.picking_policy:
                policies_multi_savings[policy_name] = (1 - (eff.total_energy_consumed / eff.current_energy_consumed)) * 100
                #measurements
                on_machines = []
                for index, measurement in enumerate(exp_result.measurements):
                    if index < len(exp_result.measurements)-500:
                        on_machines.append(measurement.machinesOn)
                policies_multi_on_machines[policy_name] = on_machines
                #kwh
                policies_multi_kw[policy_name] = eff.kwh_saved_per_shutting
                #idle
                policies_multi_idle[policy_name] = (eff.avg_number_machines_on/10000 - max(exp_result.cell_state_avg_cpu_utilization, exp_result.cell_state_avg_mem_utilization))*100
                #queuetimes
                for workload_stat in exp_result.workload_stats:
                    if workload_stat.workload_name == "Service":
                        policies_multi_service_90p_first[policy_name] = workload_stat.job_queue_time_till_first_scheduled_90_percentile
                        policies_multi_service_90p_fully[policy_name] = workload_stat.job_queue_time_till_fully_scheduled_90_percentile
                        #job think time
                        policies_multi_service_think[policy_name] = workload_stat.job_think_times_90_percentile
                    elif workload_stat.workload_name == "Batch":
                        policies_multi_batch_think[policy_name] = workload_stat.job_think_times_90_percentile
                        epochs = []
                        for epoch in workload_stat.epochs:
                            epochs.append(epoch.fintess_avg)
                            policies_multi_epochs[policy_name] = epochs

policies_dict_name_legend = collections.OrderedDict(sorted(policies_dict_name_legend.items()))
policies_single_savings = collections.OrderedDict(sorted(policies_single_savings.items()))
policies_multi_savings = collections.OrderedDict(sorted(policies_multi_savings.items()))
policies_single_batch_think = collections.OrderedDict(sorted(policies_single_batch_think.items()))
policies_multi_batch_think = collections.OrderedDict(sorted(policies_multi_batch_think.items()))
policies_single_service_think = collections.OrderedDict(sorted(policies_single_service_think.items()))
policies_multi_service_think = collections.OrderedDict(sorted(policies_multi_service_think.items()))
policies_single_kw = collections.OrderedDict(sorted(policies_single_kw.items()))
policies_multi_kw = collections.OrderedDict(sorted(policies_multi_kw.items()))
policies_single_idle = collections.OrderedDict(sorted(policies_single_idle.items()))
policies_multi_idle = collections.OrderedDict(sorted(policies_multi_idle.items()))
policies_single_service_90p_first = collections.OrderedDict(sorted(policies_single_service_90p_first.items()))
policies_multi_service_90p_first = collections.OrderedDict(sorted(policies_multi_service_90p_first.items()))
policies_single_service_90p_fully = collections.OrderedDict(sorted(policies_single_service_90p_fully.items()))
policies_multi_service_90p_fully = collections.OrderedDict(sorted(policies_multi_service_90p_fully.items()))
policies_single_on_machines = collections.OrderedDict(sorted(policies_single_on_machines.items()))
policies_multi_on_machines = collections.OrderedDict(sorted(policies_multi_on_machines.items()))
policies_single_epochs = collections.OrderedDict(sorted(policies_single_epochs.items()))
policies_multi_epochs = collections.OrderedDict(sorted(policies_multi_epochs.items()))
#kwh




N = len(policies_single_epochs.keys())
figure = plt.figure(figsize=(11, 8))
plt.rcParams.update({'font.size': 25})
plt.ylabel('Job energy consumption (kWh)')
plt.xlabel('# Epoch')

marker = itertools.cycle((',', '+', '.', 'o', '*'))
color = itertools.cycle(('b', 'g', 'r', 'y', 'p'))
#linestyle = itertools.cycle((':', '-.', '--', '-'))
color = itertools.cycle('k')
linestyle = itertools.cycle('--')
for key, value in policies_single_epochs.iteritems():
    #ax1.plot(value,linestyle='--', marker='', markersize=10, color='#ff9626', linewidth=3)
    plt.plot(value, linestyle=linestyle.next(), color='k', linewidth=2, label=policies_dict_name_legend.get(key))
#plt.legend(bbox_to_anchor=(0., 1.02, 1., .102), loc=3,
          #ncol=7, mode="expand", borderaxespad=0.)
#plt.tight_layout()
#plt.show()
figure.savefig(os.path.join(input_dir,'monoliticfitnessevolutiosingle.pdf'), format='PDF')



#Empieza el multi
#
#
#
N = len(policies_single_epochs.keys())
figure = plt.figure(figsize=(11, 8))
plt.rcParams.update({'font.size': 25})
plt.ylabel('Job energy consumption (kWh)')
plt.xlabel('# Epoch')

marker = itertools.cycle((',', '+', '.', 'o', '*'))
color = itertools.cycle(('b', 'g', 'r', 'y', 'p'))
#linestyle = itertools.cycle((':', '-.', '--', '-'))
linestyle = itertools.cycle('--')
for key, value in policies_multi_epochs.iteritems():
    #ax1.plot(value,linestyle='--', marker='', markersize=10, color='#ff9626', linewidth=3)
    plt.plot(value, linestyle=linestyle.next(), color='k', linewidth=2, label=policies_dict_name_legend.get(key))
#plt.legend(bbox_to_anchor=(0., 1.02, 1., .102), loc=3,
#          ncol=7, mode="expand", borderaxespad=0.)
#plt.tight_layout()
#plt.show()
figure.savefig(os.path.join(input_dir,'monoliticfitnessevolutionmulti.pdf'), format='PDF')