import sys, os, re
import logging
import numpy as np
from collections import defaultdict
import cluster_simulation_protos_pb2
#import matplotlib
#matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
import itertools
from math import *
from matplotlib.collections import LineCollection
from matplotlib.colors import ListedColormap, BoundaryNorm


def plot_colourline(x, y, c):
    ax = plt.gca()
    for i in np.arange(len(x) - 1):
        ax.plot([x[i], x[i + 1]], [y[i], y[i + 1]], 'r' if c[i] == "Mesos" else 'b')
    return


def uniqueish_color():
    """There're better ways to generate unique colors, but this isn't awful."""
    return plt.cm.gist_ncar(np.random.random())


#input_dirs = ("/Users/damianfernandez/IdeaProjects/score/experiment_results/joseA25IAdiscernerW03all",
#              "/Users/damianfernandez/IdeaProjects/score/experiment_results/joseA25IAdiscernerW05all",
#              "/Users/damianfernandez/IdeaProjects/score/experiment_results/joseA25IAdiscernerW07all")
#input_dirs = ("/Users/damianfernandez/IdeaProjects/score/experiment_results/joseA25IAdiscernerWdynamicall",)
input_dirs = ("/Users/damianfernandez/IdeaProjects/score/experiment_results/boost-w05/A25IA80-120W05MP120",)
input_protobuff_dynamic = ""
input_protobuff_mesos = ""
input_protobuff_omega = ""

for base_dir in input_dirs:
    for fn in os.listdir(base_dir):
        if os.path.splitext(fn)[1] == ".protobuf":
            if fn.startswith("dynamic"):
                input_protobuff_dynamic = os.path.join(base_dir, fn)
            elif fn.startswith("google-mesos"):
                input_protobuff_mesos = os.path.join(base_dir, fn)
            elif fn.startswith("google-omega-resource-fit-all-or-nothing"):
                input_protobuff_omega = os.path.join(base_dir, fn)

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

    # experiments_to_plot = [number for number in range(25)]
    experiments_to_plot = [number for number in range(5)]
    for experiment in experiments_to_plot:
        envs_to_plot = (experiment * 3, experiment * 3 + 1, experiment * 3 + 2)
        input_dir = base_dir + "/_figuras/" + str(experiment) + "/"
        for env_number in envs_to_plot:
            inter_mean = []
            fully_mean = {'Dynamic': [], 'Mesos': [], 'Omega': []}
            first_mean = {'Dynamic': [], 'Mesos': [], 'Omega': []}
            sched_mean = {'Dynamic': [], 'Mesos': [], 'Omega': []}
            rms = []
            colors = []
            env = experiment_result_set_dynamic.experiment_env[env_number]
            for exp_result in env.experiment_result:
                for measurement in exp_result.measurements:
                    inter_mean.append(measurement.interMean)
                    fully_mean['Dynamic'].append(measurement.queuefullyBatch)
                    first_mean['Dynamic'].append(measurement.queuefirstBatch)
                    sched_mean['Dynamic'].append(measurement.schedulingTimeBatch)
                    rms.append(measurement.strategy)
                break
            env = experiment_result_set_mesos.experiment_env[env_number]
            # for env in experiment_result_set_mesos.experiment_env:
            for exp_result in env.experiment_result:
                for measurement in exp_result.measurements:
                    fully_mean['Mesos'].append(measurement.queuefullyBatch)
                    first_mean['Mesos'].append(measurement.queuefirstBatch)
                    sched_mean['Mesos'].append(measurement.schedulingTimeBatch)
                break

            env = experiment_result_set_omega.experiment_env[env_number]
            # for env in experiment_result_set_omega.experiment_env:
            for exp_result in env.experiment_result:
                for measurement in exp_result.measurements:
                    fully_mean['Omega'].append(measurement.queuefullyBatch)
                    first_mean['Omega'].append(measurement.queuefirstBatch)
                    sched_mean['Omega'].append(measurement.schedulingTimeBatch)
                break
            days_to_plot = ((0, 15), (0, 4), (6, 10))
            y_lims = ((0, 800), (0, 400), (0, 200))
            for day_tuple in days_to_plot:
                for y_lim in y_lims:
                    input_dir = base_dir + "/_figuras/" + str(experiment) + "/y_lim" + str(y_lim[1])+"/"
                    if not os.path.exists(os.path.join(input_dir)):
                        os.makedirs(os.path.join(input_dir))
                    # N = len(policies_dict_name_legend.keys())
                    N = 1
                    #figure = plt.figure(figsize=(1, 3), num=10)
                    #figure.clf()
                    plt.rcParams.update({'font.size': 35})
                    # ind = np.arange(N)  # the x locations for the groups
                    # width = 0.35
                    # ax1 = figure.add_subplot(1, 1, 1, position = [0.1, 0.2, 0.75, 0.75])
                    figure, ax1 = plt.subplots(figsize=(40, 10), num=10, clear=True)
                    ax1.cla()
                    ax1.margins(0)
                    ax1.set_ylabel('Queue fully (s)')
                    ax1.set_xlabel('# Day')
                    # ax1.set_xticklabels(policies_dict_name_legend.values())
                    runtime = 86400.0 * 15
                    tickfrequency = 60.0
                    numberDays = 15.0
                    rangeDayStart = day_tuple[0]
                    rangeDayEnd = day_tuple[1]
                    dailyTicks = int(len(fully_mean['Mesos']) / numberDays)
                    tickStart = int(rangeDayStart * dailyTicks)
                    tickEnd = int(rangeDayEnd * dailyTicks)
                    # print(tickStart, tickEnd)
                    # for i in np.arange(tickStart, tickEnd):
                    #     ax1.plot([x[i], x[i + 1]], [y[i], y[i + 1]], colors[i])
                    marker = itertools.cycle((',', '+', '.', 'o', '*'))
                    color = itertools.cycle(('b', 'g', 'r', 'y', 'p'))
                    linestyle = itertools.cycle(('-.', '-', '--', '-'))
                    for key, value in fully_mean.items():
                        # ax1.plot(value,linestyle='--', marker='', markersize=10, color='#ff9626', linewidth=3)
                        ax1.plot(value[tickStart:tickEnd], linestyle=next(linestyle), marker=next(marker), markersize=2,
                                 linewidth=3, label=key)
                    # ax1.plot(cpu_util, linestyle='-', linewidth=1)
                    ax1.set_ylim([y_lim[0], y_lim[1]])
                    numberDaysPeriod = rangeDayEnd - rangeDayStart
                    xtickmin = plt.xticks()[0][0]
                    xtickmax = plt.xticks()[0][-1]
                    dailyTicks = int((xtickmax - xtickmin) / numberDaysPeriod)
                    ticks = [ceil(dailyTicks * number) for number in range(0, numberDaysPeriod + 1)]
                    plt.xticks(ticks, range(rangeDayStart, int(rangeDayEnd + 1)))
                    # plt.yticks([0.05, 0.1, 0.15, 0.2, 0.25], ['50', '100', '150', '200', '250'])
                    # plt.yticks([0.3, 0.4, 0.5], ['30', '40', '50'])
                    ax1.legend()
                    plt.tight_layout()
                    inter_arrival_name = '80'
                    if (env_number % 3 == 1):
                        inter_arrival_name = '100'
                    elif (env_number % 3 == 2):
                        inter_arrival_name = '120'
                    name_string = 'IA' + inter_arrival_name + "D" + str(rangeDayStart) + "-" + str(rangeDayEnd)
                    figure.savefig(os.path.join(input_dir + 'queue_fully_evolution_comparison' + name_string + '.pdf'),
                                   format='PDF')

                    # intermeanmeasurementcomparisondynamic
                    N = 1
                    #figure = plt.figure(figsize=(1, 3), num=11)
                    #figure.clf()
                    plt.rcParams.update({'font.size': 35})
                    # ind = np.arange(N)  # the x locations for the groups
                    # width = 0.35
                    # ax1 = figure.add_subplot(1, 1, 1, position = [0.1, 0.2, 0.75, 0.75])
                    figure, ax1 = plt.subplots(figsize=(40, 10), num=11, clear=True)
                    ax1.margins(0)
                    ax1.set_ylabel('Inter-arrival (s)')
                    ax1.set_xlabel('# Day')
                    # ax1.set_xticklabels(policies_dict_name_legend.values())
                    x = np.arange(0, len(inter_mean))
                    y = np.asarray(inter_mean)
                    colors = ['r' if rm == "Mesos" else 'b' for rm in rms]
                    dailyTicks = int(len(inter_mean) / numberDays)
                    tickStart = int(rangeDayStart * dailyTicks)
                    tickEnd = int(rangeDayEnd * dailyTicks)
                    for i in np.arange(tickStart, tickEnd):
                        ax1.plot([x[i], x[i + 1]], [y[i], y[i + 1]], colors[i], linewidth=3)
                    ax1.set_ylim([y_lim[0], y_lim[1]])
                    runTimePeriod = (rangeDayEnd - rangeDayStart) * 86400.0
                    numberDaysPeriod = rangeDayEnd - rangeDayStart
                    ticks = [ceil(dailyTicks * number) for number in range(rangeDayStart, rangeDayEnd + 1)]
                    plt.xticks(ticks, range(rangeDayStart, int(rangeDayEnd + 1)))
                    plt.tight_layout()
                    figure.savefig(os.path.join(input_dir + 'interevolutiondynamic' + name_string + '.pdf'),
                                   format='PDF')

                    # queueFirstMeasurementComparisonDynamic

                    # N = len(policies_dict_name_legend.keys())
                    N = 1
                    #figure = plt.figure(figsize=(1, 3), num=12)
                    #figure.clf()
                    plt.rcParams.update({'font.size': 35})
                    # ind = np.arange(N)  # the x locations for the groups
                    # width = 0.35
                    # ax1 = figure.add_subplot(1, 1, 1, position = [0.1, 0.2, 0.75, 0.75])
                    figure, ax1 = plt.subplots(figsize=(40, 10), num=12, clear=True)
                    ax1.margins(0)
                    ax1.set_ylabel('Queue first (s)')
                    ax1.set_xlabel('# Day')
                    # ax1.set_xticklabels(policies_dict_name_legend.values())
                    dailyTicks = int(len(first_mean['Mesos']) / numberDays)
                    tickStart = int(rangeDayStart * dailyTicks)
                    tickEnd = int(rangeDayEnd * dailyTicks)
                    # print(tickStart, tickEnd)
                    # for i in np.arange(tickStart, tickEnd):
                    #     ax1.plot([x[i], x[i + 1]], [y[i], y[i + 1]], colors[i])
                    marker = itertools.cycle((',', '+', '.', 'o', '*'))
                    color = itertools.cycle(('b', 'g', 'r', 'y', 'p'))
                    linestyle = itertools.cycle(('-.', '-', '--', '-'))
                    for key, value in first_mean.items():
                        # ax1.plot(value,linestyle='--', marker='', markersize=10, color='#ff9626', linewidth=3)
                        ax1.plot(value[tickStart:tickEnd], linestyle=next(linestyle), marker=next(marker), markersize=2,
                                 linewidth=3, label=key)
                    # ax1.plot(cpu_util, linestyle='-', linewidth=1)
                    ax1.set_ylim([y_lim[0], y_lim[1]])
                    numberDaysPeriod = rangeDayEnd - rangeDayStart
                    xtickmin = plt.xticks()[0][0]
                    xtickmax = plt.xticks()[0][-1]
                    dailyTicks = int((xtickmax - xtickmin) / numberDaysPeriod)
                    ticks = [ceil(dailyTicks * number) for number in range(0, numberDaysPeriod + 1)]
                    plt.xticks(ticks, range(rangeDayStart, int(rangeDayEnd + 1)))
                    # plt.yticks([0.05, 0.1, 0.15, 0.2, 0.25], ['50', '100', '150', '200', '250'])
                    # plt.yticks([0.3, 0.4, 0.5], ['30', '40', '50'])
                    ax1.legend()
                    plt.tight_layout()
                    figure.savefig(os.path.join(input_dir + 'queue_first_evolution_comparison' + name_string + '.pdf'),
                                   format='PDF')

                    # schedulingTimeMeasurementComparisonDynamic

                    # N = len(policies_dict_name_legend.keys())
                    N = 1
                    # figure = plt.figure(figsize=(1, 3), num=12)
                    # figure.clf()
                    plt.rcParams.update({'font.size': 35})
                    # ind = np.arange(N)  # the x locations for the groups
                    # width = 0.35
                    # ax1 = figure.add_subplot(1, 1, 1, position = [0.1, 0.2, 0.75, 0.75])
                    figure, ax1 = plt.subplots(figsize=(40, 10), num=12, clear=True)
                    ax1.margins(0)
                    ax1.set_ylabel('Scheduling time (s)')
                    ax1.set_xlabel('# Day')
                    # ax1.set_xticklabels(policies_dict_name_legend.values())
                    dailyTicks = int(len(sched_mean['Mesos']) / numberDays)
                    tickStart = int(rangeDayStart * dailyTicks)
                    tickEnd = int(rangeDayEnd * dailyTicks)
                    # print(tickStart, tickEnd)
                    # for i in np.arange(tickStart, tickEnd):
                    #     ax1.plot([x[i], x[i + 1]], [y[i], y[i + 1]], colors[i])
                    marker = itertools.cycle((',', '+', '.', 'o', '*'))
                    color = itertools.cycle(('b', 'g', 'r', 'y', 'p'))
                    linestyle = itertools.cycle(('-.', '-', '--', '-'))
                    for key, value in sched_mean.items():
                        # ax1.plot(value,linestyle='--', marker='', markersize=10, color='#ff9626', linewidth=3)
                        ax1.plot(value[tickStart:tickEnd], linestyle=next(linestyle), marker=next(marker), markersize=2,
                                 linewidth=3, label=key)
                    # ax1.plot(cpu_util, linestyle='-', linewidth=1)
                    ax1.set_ylim([y_lim[0], y_lim[1]])
                    numberDaysPeriod = rangeDayEnd - rangeDayStart
                    xtickmin = plt.xticks()[0][0]
                    xtickmax = plt.xticks()[0][-1]
                    dailyTicks = int((xtickmax - xtickmin) / numberDaysPeriod)
                    ticks = [ceil(dailyTicks * number) for number in range(0, numberDaysPeriod + 1)]
                    plt.xticks(ticks, range(rangeDayStart, int(rangeDayEnd + 1)))
                    # plt.yticks([0.05, 0.1, 0.15, 0.2, 0.25], ['50', '100', '150', '200', '250'])
                    # plt.yticks([0.3, 0.4, 0.5], ['30', '40', '50'])
                    ax1.legend()
                    plt.tight_layout()
                    figure.savefig(os.path.join(input_dir + 'scheduling_time_evolution_comparison' + name_string + '.pdf'),
                                   format='PDF')

