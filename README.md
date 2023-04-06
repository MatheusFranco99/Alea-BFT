# Alea-BFT

![](md_resources/aleabft.png)

Alea-BFT ([Alea-BFT arXiv](https://arxiv.org/abs/2202.02071)) protocol implementation in python3.


## The Protocol
Alea-BFT is an asynchronous byzantine fault tolerance protocol. Its major benefit is the quadratic communication complexity, against the cubic complexity of previous protocols. This is an important scalability upgrade from Alea-BFT which allows it to be applied in real world scenarios.

## Purpose

The purpose of this implementation is to test and take metrics of the original protocol and of variations of it.

## Usage

```console
usage: script.py [-h] [-n NODE_COUNT] [-v VERBOSE]

options:
  -h, --help            show this help message and exit
  -n NODE_COUNT, --node_count NODE_COUNT
                        node count
  -v VERBOSE, --verbose VERBOSE
                        verbose style (0: silence mode, 1: full verbose, 2:
                        log only metrics)
```
Example:
```console
python3 script.py -n 4 -v 2
```

## Documentation

Refer to the [documentation file](documentation.md) for information about how the code is structured and the purpose of each file


## Testing behavior
When the network is launched, only the node 1 starts a VCBC. Node 1 starts new VCBCs after $n*0.07$ seconds where $n$ is the number of nodes.
Note that this is implemented to test latency instead of throughput.

## Metrics analysis
To analyse the outputs, [analysis/analyzer.py](analysis/analyzer.py) was created. Refer to its [documentation](analysis/README.md) for more details.


## Roadmap:
- [X] Alea-BFT base implementation
- [ ] Threshold signture schema


