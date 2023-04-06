# Analysis

## Usage
```console
usage: analyzer.py [-h] [--list LIST [LIST ...]] {single_execution,multiple_executions,get_total_time,compare_means} ...

positional arguments:
  {single_execution,multiple_executions,get_total_time,compare_means}

options:
  -h, --help            show this help message and exit
  --list LIST [LIST ...]
```

## Single execution command
```console
usage: analyzer.py single_execution [-h] -f FILENAME -o OUTPUT_FILE

options:
  -h, --help            show this help message and exit
  -f FILENAME, --filename FILENAME
                        file name
  -o OUTPUT_FILE, --output_file OUTPUT_FILE
                        output file name for graphic
```
Analyse the log in the input file and creates a chart with the latency values, the mean latency and its standard deviation.
E.g.:
```bash
python3 analyzer.py single_execution -f n4_40.log -o chart.png
```


### Multiple executions command
```console
usage: analyzer.py multiple_executions [-h] -f FILENAMES [FILENAMES ...] [-l LABELS [LABELS ...]] -o OUTPUT_FILE [-m]

options:
  -h, --help            show this help message and exit
  -f FILENAMES [FILENAMES ...], --filenames FILENAMES [FILENAMES ...]
                        name of log files
  -l LABELS [LABELS ...], --labels LABELS [LABELS ...]
                        label names
  -o OUTPUT_FILE, --output_file OUTPUT_FILE
                        output file name for graphic
  -m, --mean            plot mean instead of values
```
Get latency list on multiple files, calculate their means (if -m is set) and plots this in a chart with --labels. E.g.:
```bash
python3 analyzer.py multiple_executions -f n4_40.log n7_40.log -l 4 7 -o chart.png
```

### Get total time command
```console
usage: analyzer.py get_total_time [-h] -f FILENAME

options:
  -h, --help            show this help message and exit
  -f FILENAME, --filename FILENAME
                        file name
```
Analyse log to get the total execution time. Prints the value calculated and also the number of instances terminated by the total time. E.g.:
```bash
python3 analyzer.py get_total_time -f n4_40.log
```

### Compare means command
```console
usage: analyzer.py compare_means [-h] -f FILENAMES [FILENAMES ...] -n NODE_NUMBERS [NODE_NUMBERS ...] -o OUTPUT_FILE

options:
  -h, --help            show this help message and exit
  -f FILENAMES [FILENAMES ...], --filenames FILENAMES [FILENAMES ...]
                        name of log files
  -n NODE_NUMBERS [NODE_NUMBERS ...], --node_numbers NODE_NUMBERS [NODE_NUMBERS ...]
                        node numbers
  -o OUTPUT_FILE, --output_file OUTPUT_FILE
                        output file name for graphic
```
Analyse the log in each file and take the mean latency for each file. Then, creates a list with the means, finds the best fist polynom and plot it with the means. At last, perform an ANOVA statistical test to verify if the means follow a quadratic polynom.  E.g.:
```bash
python3 analyzer.py compare_means -f n4_40.log n7_40.log n13_40.log -n 4 7 13 -o chart.png
```
