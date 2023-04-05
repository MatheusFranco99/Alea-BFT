import subprocess
import signal
import sys
import os

N = int(sys.argv[1])

# Create a list to hold the Popen objects
node_procs = []

# # Kill all processes running on ports 1350 to 135N-1
# for i in range(1351, 1350+N+1):
#     cmd = f'lsof -t -i tcp:{i} | xargs kill -9'
#     os.system(cmd)

# Launch the node.py processes
for i in range(1, N+1):
    out_file = open(f"out{i}.txt", "w")
    proc = subprocess.Popen(
        ["python3", "node.py", str(i), str(N)],
        stdout=out_file,
        stderr=out_file,
    )
    node_procs.append(proc)

# Define the signal handler function
def signal_handler(sig, frame):
    # Loop through the Popen objects and terminate them
    for proc in node_procs:
        proc.terminate()
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
