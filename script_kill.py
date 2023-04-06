import subprocess
import signal
import sys
import os

N = int(sys.argv[1])

# # Kill all processes running on ports 1350 to 135N-1
def kill_process_mac(port):
    cmd = f'lsof -t -i tcp:{port} | xargs kill -9'
    os.system(cmd)

def kill_process_linux(port):
    try:
        output = subprocess.check_output(["lsof", "-i", f"TCP:{port}"])
    except subprocess.CalledProcessError:
        return
    lines = output.decode().split('\n')
    for line in lines[1:]:
        if line.strip() == '':
            continue
        fields = line.split()
        pid = fields[1]
        os.kill(int(pid), signal.SIGKILL)


for port in range(1351, 1350+N+1):
    kill_process_linux(port)