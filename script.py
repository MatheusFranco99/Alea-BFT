import subprocess
import signal
from signal import SIGINT
import sys
import os
import argparse



# N = int(sys.argv[1])

# verbose_mode = int(sys.argv[2])

parser = argparse.ArgumentParser()
parser.add_argument('-n', '--node_count', type=int, help='node count')
parser.add_argument('-v', '--verbose', type=int, required = False, help='verbose style (0: silence mode, 1: full verbose, 2: log only metrics)')
parser.add_argument('-t', '--time', type=float, required = False, help='time in seconds that the execution will run (after startup)')
parser.add_argument('-c', '--counter', type=int, required = True, help='number of transactions (VCBC counter)')
parser.add_argument('-d', '--delay', type=float, required = False, help='delay between transactions (in milliseconds)')


args = parser.parse_args()

N = args.node_count
verbose_mode = 2
if args.verbose != None:
    verbose_mode = args.verbose

if verbose_mode not in [0,1,2]:
    raise Exception("Verbose mode should be 0, 1 or 2")

exec_time = None
if args.time != None:
    exec_time = args.time

transactions_num = args.counter

delay = args.delay

# Create a list to hold the Popen objects
node_procs = []

# Launch the node.py processes
for i in range(1, N+1):
    # out_file = open(f"out{i}.log", "w")
    command = ["python3", "node.py","launch", "-id",str(i),"-n", str(N),"-v",str(verbose_mode),"-c",str(transactions_num)]

    if exec_time != None:
        command = command + ["-t",str(exec_time)]
    if delay != None:
        command = command + ["-d",str(delay)]

    proc = subprocess.Popen(
        command,
        # stdout=out_file,
        # stderr=out_file,
    )
    node_procs.append(proc)

# Define the signal handler function
def signal_handler(sig, frame):
    # Loop through the Popen objects and terminate them
    for proc in node_procs:
        proc.send_signal(SIGINT)
        # proc.terminate()
    for proc in node_procs:
        proc.wait()
    sys.exit(0)

# Set the signal handler for CTRL+C
signal.signal(signal.SIGINT, signal_handler)

# Wait for the node.py processes to finish
for proc in node_procs:
    proc.wait()

# Close the output files
# for i in range(1, N+1):
#     out_file = open(f"out{i}.txt", "a")
#     out_file.write("Done\n")
#     out_file.close()
