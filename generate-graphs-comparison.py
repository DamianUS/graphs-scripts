import sys, os
import logging
import numpy as np
from mpl_toolkits.mplot3d import axes3d, Axes3D #<-- Note the capitalization!
import collections
import cluster_simulation_protos_pb2
import matplotlib.pyplot as plt
import itertools
from math import *
import re
from matplotlib import cm

from scipy.interpolate import griddata



def usage():
    print "Usage: Input 1 Dir of protobuf"
    sys.exit(1)

logging.debug("len(sys.argv): " + str(len(sys.argv)))

if len(sys.argv) < 1:
    logging.error("Not enough arguments provided.")
    usage()

try:
    input_dir = sys.argv[1]

except:
    usage()
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

for env in experiment_result_set_single.experiment_env:
    for exp_result in env.experiment_result:
        eff = exp_result.efficiency_stats
        str_ar = filter(None, re.split("[\-!?:]+", eff.power_off_policy.name))
        threshold = float(str_ar[6])
        lost = float(str_ar[10])
        #if any(policy_name in eff.power_off_policy.name for policy_name in policies_dict_name_legend.keys()):
        policies_single_savings[(threshold, lost)] = (1 - (eff.total_energy_consumed / eff.current_energy_consumed)) * 100
        # #measurements
        # on_machines = []
        # for index, measurement in enumerate(exp_result.measurements):
        #     if index < len(exp_result.measurements) - 500:
        #         on_machines.append(measurement.machinesOn)
        # policies_single_on_machines[policy_name] = on_machines
        #kwh
        policies_single_kw[(threshold, lost)] = eff.kwh_saved_per_shutting
        #idle
        policies_single_idle[(threshold, lost)] = (eff.avg_number_machines_on / 10000 - max(
            exp_result.cell_state_avg_cpu_utilization, exp_result.cell_state_avg_mem_utilization)) * 100
        for workload_stat in exp_result.workload_stats:
            if workload_stat.workload_name == "Service":
                # queue times
                policies_single_service_90p_first[(threshold, lost)] = workload_stat.job_queue_time_till_first_scheduled_90_percentile
                policies_single_service_90p_fully[(threshold, lost)] = workload_stat.job_queue_time_till_fully_scheduled_90_percentile
                #job think time
                policies_single_service_think[(threshold, lost)] = workload_stat.job_think_times_90_percentile
            elif workload_stat.workload_name == "Batch":
                    policies_single_batch_think[(threshold, lost)] = workload_stat.job_think_times_90_percentile

print("Empieza a leer multi")
multi_infile = open(input_protobuff_monolithic_multi, "rb")
experiment_result_set_multi.ParseFromString(multi_infile.read())
multi_infile.close()
print("Termina de leer multi")

for env in experiment_result_set_multi.experiment_env:
    for exp_result in env.experiment_result:
        eff = exp_result.efficiency_stats
        str_ar = filter(None, re.split("[\-!?:]+", eff.power_off_policy.name))
        threshold = float(str_ar[6])
        lost = float(str_ar[10])
        policies_multi_savings[(threshold, lost)] = (1 - (eff.total_energy_consumed / eff.current_energy_consumed)) * 100
        #measurements
        # on_machines = []
        # for index, measurement in enumerate(exp_result.measurements):
        #     if index < len(exp_result.measurements)-500:
        #         on_machines.append(measurement.machinesOn)
        # policies_multi_on_machines[policy_name] = on_machines
        #kwh
        policies_multi_kw[(threshold, lost)] = eff.kwh_saved_per_shutting
        #idle
        policies_multi_idle[(threshold, lost)] = (eff.avg_number_machines_on/10000 - max(exp_result.cell_state_avg_cpu_utilization, exp_result.cell_state_avg_mem_utilization))*100
        #queuetimes
        for workload_stat in exp_result.workload_stats:
            if workload_stat.workload_name == "Service":
                policies_multi_service_90p_first[(threshold, lost)] = workload_stat.job_queue_time_till_first_scheduled_90_percentile
                policies_multi_service_90p_fully[(threshold, lost)] = workload_stat.job_queue_time_till_fully_scheduled_90_percentile
                #job think time
                policies_multi_service_think[(threshold, lost)] = workload_stat.job_think_times_90_percentile
            elif workload_stat.workload_name == "Batch":
                policies_multi_batch_think[(threshold, lost)] = workload_stat.job_think_times_90_percentile


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
#kwh

dict_figuras = {}
dict_figuras[("policies_single_savings", "Total Savings %")] = policies_single_savings
dict_figuras[("policies_multi_savings", "Total Savings %")] = policies_multi_savings
dict_figuras[("policies_single_batch_think", "Job think time (s)")] = policies_single_batch_think
dict_figuras[("policies_multi_batch_think", "Job think time (s)")] = policies_multi_batch_think
dict_figuras[("policies_single_service_think", "Job think time (s)")] = policies_single_service_think
dict_figuras[("policies_multi_service_think", "Job think time (s)")] = policies_multi_service_think
dict_figuras[("policies_single_kw", "kWh saved per shutting")] = policies_single_kw
dict_figuras[("policies_multi_kw", "kWh saved per shutting")] = policies_multi_kw
dict_figuras[("policies_single_idle", "Idle resources (%)")] = policies_single_idle
dict_figuras[("policies_multi_idle", "Idle resources (%)")] = policies_multi_idle
dict_figuras[("policies_single_service_90p_first", "Job queue time (s)")] = policies_single_service_90p_first
dict_figuras[("policies_multi_service_90p_first", "Job queue time (s)")] = policies_multi_service_90p_first
dict_figuras[("policies_single_service_90p_fully", "Job queue time (s)")] = policies_single_service_90p_fully
dict_figuras[("policies_multi_service_90p_fully", "Job queue time (s)")] = policies_multi_service_90p_fully


def fun(tuple, dictionary):
  return dictionary.get((tuple[0], tuple[1]))


for key, value in dict_figuras.iteritems():
    keys = value.keys()
    X1 = list(set([float(i[0]) for i in keys]))
    Y1 = list(set([float(i[1]) for i in keys]))
    X1.sort()
    Y1.sort()
    X, Y = np.meshgrid(X1, Y1)
    Z = np.array([fun(tuple, value) for tuple in list(itertools.product(X1, Y1))]).reshape(
        np.array(X).shape)
    fig = plt.figure()
    ax = Axes3D(fig)
    ax.plot_surface(X, Y, Z, rstride=3, cstride=3, alpha=0.3, cmap=cm.cool)
    ax.set_xlabel('Distribution decision threshold')
    ax.set_ylabel('Lost resources factor')
    ax.set_zlabel(key[1])
    ax.view_init(elev=25, azim=-58)  # elevation and angle
    ax.dist = 11  # distance
    fig.savefig(os.path.join(input_dir, key[0]+'.pdf'), format='PDF')


