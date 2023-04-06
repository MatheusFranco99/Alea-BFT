# Analysis

## Usage
```console
usage: analyzer.py [-h] [--list LIST [LIST ...]] {add,plot} ...

positional arguments:
  {add,plot}

options:
  -h, --help            show this help message and exit
  --list LIST [LIST ...]
```

## Add command
```console
usage: analyzer.py add [-h] -f FILENAMES [FILENAMES ...] -n NUMBER_OF_NODES

options:
  -h, --help            show this help message and exit
  -f FILENAMES [FILENAMES ...], --filenames FILENAMES [FILENAMES ...]
                        file names
  -n NUMBER_OF_NODES, --number_of_nodes NUMBER_OF_NODES
                        number of nodes
```
Analyse log info contained in the several files, related to number of nodes $n$, and stores this info into a persistent memory with pickle.
E.g.:
```bash
python3 analyzer.py add -n 4 -f logs/n4*
```
This command adds logs info contained in all files logs/n4* and links them with $n=4$.


### Multiple executions command
```console
usage: analyzer.py plot [-h] -n NUMBER_OF_NODES [NUMBER_OF_NODES ...] -o OUTPUT_FILE

options:
  -h, --help            show this help message and exit
  -n NUMBER_OF_NODES [NUMBER_OF_NODES ...], --number_of_nodes NUMBER_OF_NODES [NUMBER_OF_NODES ...]
                        list with number of nodes to show
  -o OUTPUT_FILE, --output_file OUTPUT_FILE
                        output file name for chart
```
Receives a list of number of nodes and plots the latency by throughput chart. E.g.:
```bash
python3 analyzer.py plot -o t_l.png -n 4 7 13
```
This command plots the latency by throughput curve with info about $n=4$, $n=7$ and $n=13$.
