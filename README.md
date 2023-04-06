# Alea-BFT

<p align="center">
  <img src="md_resources/aleabft.png">
</p>

<!-- ![](md_resources/aleabft.png) -->

Alea-BFT ([Alea-BFT arXiv](https://arxiv.org/abs/2202.02071)) protocol implementation in python3.


## The Protocol
Alea-BFT is an asynchronous byzantine fault tolerance protocol. Its major benefit is the quadratic communication complexity, against the cubic complexity of previous protocols. This is an important scalability upgrade from Alea-BFT which allows it to be applied in real world scenarios.

## Purpose

The purpose of this implementation is to test and take metrics of the original protocol and of variations of it.

## Usage

```console
usage: script.py [-h] [-n NODE_COUNT] [-v VERBOSE] [-t TIME] -c COUNTER [-d DELAY]

options:
  -h, --help            show this help message and exit
  -n NODE_COUNT, --node_count NODE_COUNT
                        node count
  -v VERBOSE, --verbose VERBOSE
                        verbose style (0: silence mode, 1: full verbose, 2: log only metrics)
  -t TIME, --time TIME  time in seconds that the execution will run (after startup)
  -c COUNTER, --counter COUNTER
                        number of transactions (VCBC counter)
  -d DELAY, --delay DELAY
                        delay between transactions (in milliseconds)
```
- The $n$ parameter sets the number of nodes in the network.
- The optional parameter $t$ sets the maximum execution time before quitting.
- The optioal parameter $d$ sets the delay between the delivery of transactions.
- The required parameter $c$ sets the number of transactions to be delivered before quiting the application.

Note that the delay, if not set, is set to a default value (discussed below). If the total time is not set, the program ends after the $c$ transactions are terminated.

Example of command to analyse latency:
```console
python3 script.py -n 4 -v 2 -c 20 -d 5
```
Example of command to analyse throughput:
```console
python3 script.py -n 4 -v 2 -c 10000 -t 5 -d 5
```


## Documentation

Refer to the [documentation file](documentation.md) for information about how the code is structured and the purpose of each file


## Delay
If the delay is not set, there are two possibilities.
- If the total time is set, the delay is set to $total time / (num_transactions + 1)$.
- If the total time is not set, the delay is set to $n*0.07$ seconds where $n$ is the number of nodes.

## Metrics analysis
Both latency and throughput can be analysed. Refer to this [documentation](latency_analysis/README.md) for the latency analysis program and to this [documentation](throughput_analysis/README.md) for the throughput analysis program.

## Roadmap:
- [X] Alea-BFT base implementation
- [ ] Threshold signture schema


