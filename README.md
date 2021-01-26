# Parallel Climate Forcasting

## About Me

- Josh Poole
    - Senior studying Computer Science at University of Cincinnati
    - [poolejd@mail.uc.edu](mailto:poolejd@mail.uc.edu)

## The Project

A parallel implementation of rudimentary climate forcasting. Uses map reduce strategies to query a large amount of climate data, and create averages and predictions from that data. My Parallel implementation were tested against a sequential implementation on two different machines:

- My local machine which features an Intel i5-8400 running at 2.80 GHz with an available 6 cores for processing. 
- An *Owens* node using the [Ohio Supercomputer Center](https://www.osc.edu/). This node features a NVIDIA Tesla P100 GPU with an available 28 cores

My parallel implementation showed significant time run time improvement over sequential in both cases, boasting over 3x and 17x speed increases respectively.

The acutal results of my climate forcaster can be seen in [temp_data.png](temp_data.png).

Please see my [report](report/Final_Project_Report.pdf) for a more in depth write up.
