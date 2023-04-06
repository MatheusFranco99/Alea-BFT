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


args = parser.parse_args()

N = args.node_count
verbose_mode = 2
if args.verbose != None:
    verbose_mode = args.verbose

if verbose_mode not in [0,1,2]:
    raise Exception("Verbose mode should be 0, 1 or 2")

# Create a list to hold the Popen objects
node_procs = []

# Launch the node.py processes
for i in range(1, N+1):
    # out_file = open(f"out{i}.log", "w")
    proc = subprocess.Popen(
        ["python3", "node.py","launch", "-id",str(i),"-n", str(N),"-v",str(verbose_mode)],
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
