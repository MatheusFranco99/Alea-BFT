import subprocess
import signal
import sys
import os

N = int(sys.argv[1])

# # Kill all processes running on ports 1350 to 135N-1
for i in range(1351, 1350+N+1):
    cmd = f'lsof -t -i tcp:{i} | xargs kill -9'
    os.system(cmd)
