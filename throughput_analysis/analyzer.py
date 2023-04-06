import matplotlib.pyplot as plt
import argparse
import numpy as np
from datetime import datetime
import pickle
import os

pickle_file = "data.pkl"

def analyze_file(fname):
    lines = []
    with open(fname,'r') as f:
        lines = f.readlines()
    
    latencies = []
    num_executed = 0
    total_time = 0

    for line in lines:
        if "UponABAFinish" in line:
            latencies += [float(line.split('microseconds')[0].split()[-1])]
            priority = float(line.split("priority=")[1].split(')')[0])
            num_executed = max(num_executed,priority+1)
        
        if "Throughput time" in line:
            total_time = float(line.split("Throughput time: ")[1].split()[0])
    
    return {'latencies':latencies,'mean latency':sum(latencies)/len(latencies),'executions':num_executed,'throughput':num_executed/(total_time/1000000)}

def add(n,fnames):
    data = {}
    if os.path.isfile(pickle_file):
        with open(pickle_file,'rb') as f:
            data = pickle.load(f)
    
    if n in data:
        del data[n]

    data[n] = []

    for fname in fnames:
        dict_values = analyze_file(fname)
        print(dict_values)
        data[n].append(dict_values)
    
    with open(pickle_file,'wb') as f:
        pickle.dump(data,f)
    

def plot_throughput_latency(ns,output_filename):

    data = {}
    if os.path.isfile(pickle_file):
        with open(pickle_file,'rb') as f:
            data = pickle.load(f)
        
    for n in ns:
        if n not in data:
            print(f"Can't produce chart because {n=} not in {data.keys()=}.")
            return
    

    fig, ax = plt.subplots()

    def getMarker(idx):
        lst = ["x","s","o","^","p","D","8","P","*",">","<"]
        return lst[idx]

    
    for idx,n in enumerate(ns):
        n_info = data[n]
        n_info = sorted(n_info, key= lambda x: x['throughput'])

        throughputs = [x['throughput'] for x in n_info]
        latencies = [x['mean latency'] for x in n_info]

        ax.plot(throughputs,latencies)
        ax.scatter(throughputs, latencies,s=[10]*len(throughputs),marker=getMarker(idx),label=f'{n}')
        
    ax.legend()
    ax.set_title('Latency by throughput with different network size')
    ax.set_xlabel('Throughput (tx/sec)')
    ax.set_ylabel('Latency time (ms)')
    ax.grid(True)
    plt.savefig(output_filename)






parser = argparse.ArgumentParser()

subparsers = parser.add_subparsers(dest='command', required=True)

# 'add' sub-command
add_parser = subparsers.add_parser('add')
add_parser.add_argument('-f', '--filenames', type=str, required = True,nargs='+', help='file names')
add_parser.add_argument('-n', '--number_of_nodes', type=int, required = True, help='number of nodes')

# 'plot' sub-command
plot_parser = subparsers.add_parser('plot')
plot_parser.add_argument('-n', '--number_of_nodes', type=int, required = True,nargs='+', help='list with number of nodes to show')
plot_parser.add_argument('-o', '--output_file', type=str, required = True, help='output file name for chart')


# # 'multiple_executions' sub-command
# multiple_executions_parser = subparsers.add_parser('multiple_executions')
# multiple_executions_parser.add_argument('-f', '--filenames', type=str, required = True,nargs='+', help='name of log files')
# multiple_executions_parser.add_argument('-l', '--labels', type=str, required = False,nargs='+', help='label names')
# multiple_executions_parser.add_argument('-o', '--output_file', type=str, required = True, help='output file name for graphic')
# multiple_executions_parser.add_argument('-m', '--mean',  action='store_true', required = False, help='plot mean instead of values')

# # 'get_total_time' sub-command
# get_total_time_parser = subparsers.add_parser('get_total_time')
# get_total_time_parser.add_argument('-f', '--filename', type=str, required = True, help='file name')

# # 'compare_means' sub-command
# compare_means_parser = subparsers.add_parser('compare_means')
# compare_means_parser.add_argument('-f', '--filenames', type=str, required = True,nargs='+', help='name of log files')
# compare_means_parser.add_argument('-n', '--node_numbers', type=int, required = True,nargs='+', help='node numbers')
# compare_means_parser.add_argument('-o', '--output_file', type=str, required = True, help='output file name for graphic')



parser.add_argument('--list', type=str, nargs='+')

if __name__ == "__main__":

    args = parser.parse_args()

    if args.command == 'add':

        fnames = args.filenames
        n = args.number_of_nodes

        add(n,fnames)
    
    if args.command == 'plot':

        output_filename = args.output_file
        ns = args.number_of_nodes

        plot_throughput_latency(ns,output_filename)
    