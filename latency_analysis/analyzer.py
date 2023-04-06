import matplotlib.pyplot as plt
import argparse
import numpy as np
from datetime import datetime
import statsmodels.api as sm



def get_list_from_file(filename):
    with open(filename,'r') as f:
        lines = f.readlines()
    
    ans = []
    for line in lines:
        if 'microseconds' in line:
            parsed_line = line.split('microseconds')[0].split()[-1]
            ans += [float(parsed_line)/1000]
    
    return ans

def singe_execution(fname,output_filename):

    data = get_list_from_file(fname)

    # calculate mean and standard deviation for each point
    mean = np.array([np.mean(data[:i+1]) for i in range(len(data))])
    stddev = np.array([np.std(data[:i+1]) for i in range(len(data))])

    # create the plot
    fig, ax = plt.subplots()
    ax.plot(range(len(data)), data, color='red')
    ax.plot(range(len(data)), mean, color='blue')
    ax.fill_between(range(len(data)), mean+stddev, mean-stddev, alpha=0.2, color='lightblue')

    ax.set_title('Latency by agreement round')
    ax.set_xlabel('Agreement round')
    ax.set_ylabel('Time (ms)')
    ax.grid(True)
    plt.savefig(output_filename)

def multiple_executions(fnames,labels,output_filename,means):
    
    datas = []
    for fname in fnames:
        datas += [get_list_from_file(fname)]
    
    values = datas

    if means:
        values = []
        for data in datas:
            values += [np.array([np.mean(data[:i+1]) for i in range(len(data))])]
    
    fig, ax = plt.subplots()
    for i,data in enumerate(values):
        if labels != None and labels != []:
            ax.plot(range(len(data)), data,label=labels[i])
        else:
            ax.plot(range(len(data)), data)
    
    if labels != None and labels != []:
        ax.legend()

    ax.set_title('Latency by agreement round and number of nodes')
    ax.set_xlabel('Agreement round')
    ax.set_ylabel('Time (ms)')
    ax.grid(True)
    plt.savefig(output_filename)


def get_total_time(filename):
    with open(filename, "r") as f:
        first_line = f.readline().strip()
        last_line = None
        
        for line in f:
            last_line = line.strip()

        # extract time from first and last line
        first_time_str = first_line.split()[1]
        last_time_str = last_line.split()[1]
        
        # convert time strings to datetime objects
        first_time = datetime.strptime(first_time_str, "%H:%M:%S,%f")
        last_time = datetime.strptime(last_time_str, "%H:%M:%S,%f")

        # calculate time difference in seconds
        time_diff = (last_time - first_time).total_seconds() * 1000

        print(f"Time spent in milliseconds: {time_diff}")
        print(f"Number of agrements divided by time spent: {41/time_diff}")

def compare_means(fnames,node_numbers,output_filename):


    datas = []
    for fname in fnames:
        datas += [get_list_from_file(fname)]
    
    means = []
    for data in datas:
        means += [np.mean(data)]

    x = node_numbers
    y = means

    # Fit a quadratic polynomial to the data
    coeffs = np.polyfit(x, y, 2)

    # The coefficients of the polynomial
    a, b, c = coeffs

    # Print the polynomial
    print(f"Best fit polynom: y = {a}x^2 + {b}x + {c}")
    
    f = lambda x: a * x * x + b * x + c

    errors = []
    for i in range(len(x)):
        errors += [abs(y[i]-f(x[i]))]
    
    print(f"MSE (mean squared error): {sum([e*e for e in errors])/len(errors)}")
    print(f"Min error:{min(errors)}")
    print(f"Max error:{max(errors)}")
    print(f"Mean error:{sum(errors)/len(errors)}")

    fig, ax = plt.subplots()
    x_pols = list(range(0,max(x)+3))
    ax.plot(x_pols, [f(xx) for xx in x_pols],label='polynom')
    ax.scatter(x, y,s=[10]*len(x),c='red',label='mean value')
    
    ax.legend()
    ax.set_title('Mean latency and best fit polynom')
    ax.set_xlabel('number of nodes')
    ax.set_ylabel('Latency time (ms)')
    ax.grid(True)
    plt.savefig(output_filename)



    # Add a quadratic term to x
    x2 = sm.add_constant(np.column_stack((x, np.power(x, 2))))

    # Fit the model
    model = sm.OLS(y, x2).fit()

    # Print the ANOVA table
    print("ANOVA test")
    print(model.summary())



parser = argparse.ArgumentParser()

subparsers = parser.add_subparsers(dest='command', required=True)

# 'single_execution' sub-command
single_execution_parser = subparsers.add_parser('single_execution')
single_execution_parser.add_argument('-f', '--filename', type=str, required = True, help='file name')
single_execution_parser.add_argument('-o', '--output_file', type=str, required = True, help='output file name for graphic')

# 'multiple_executions' sub-command
multiple_executions_parser = subparsers.add_parser('multiple_executions')
multiple_executions_parser.add_argument('-f', '--filenames', type=str, required = True,nargs='+', help='name of log files')
multiple_executions_parser.add_argument('-l', '--labels', type=str, required = False,nargs='+', help='label names')
multiple_executions_parser.add_argument('-o', '--output_file', type=str, required = True, help='output file name for graphic')
multiple_executions_parser.add_argument('-m', '--mean',  action='store_true', required = False, help='plot mean instead of values')

# 'get_total_time' sub-command
get_total_time_parser = subparsers.add_parser('get_total_time')
get_total_time_parser.add_argument('-f', '--filename', type=str, required = True, help='file name')

# 'compare_means' sub-command
compare_means_parser = subparsers.add_parser('compare_means')
compare_means_parser.add_argument('-f', '--filenames', type=str, required = True,nargs='+', help='name of log files')
compare_means_parser.add_argument('-n', '--node_numbers', type=int, required = True,nargs='+', help='node numbers')
compare_means_parser.add_argument('-o', '--output_file', type=str, required = True, help='output file name for graphic')



parser.add_argument('--list', type=str, nargs='+')

if __name__ == "__main__":

    args = parser.parse_args()

    if args.command == 'single_execution':

        fname = args.filename
        output_filename = args.output_file
        
        singe_execution(fname,output_filename)
    
    elif args.command == 'multiple_executions':
        fnames = args.filenames
        labels = None
        if args.labels != None:
            labels = args.labels
        output_filename = args.output_file
        means = False
        if args.mean:
            means = True

        if len(labels) != len(fnames):
            print("Number of files should be equal to number of labels provided.")
        else:
            multiple_executions(fnames,labels,output_filename,means)
        
    elif args.command == 'get_total_time':
        fname = args.filename
        get_total_time(fname)
                
    elif args.command == 'compare_means':
        fnames = args.filenames
        node_numbers = args.node_numbers
        output_filename = args.output_file

        if len(node_numbers) != len(fnames):
            print("Number of files should be equal to number of number of nodes provided.")
        else:
            compare_means(fnames,node_numbers,output_filename)
