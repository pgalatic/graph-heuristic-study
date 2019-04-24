# graph-heuristic-study
A study of how well metaheuristics perform in the context of the famous graph coloring problem.

## installation

```
git clone https://github.com/somacdivad/grinpy.git
pip install -r requirements.txt
```

Sometimes the GrinPy package cannot be installed correctly. We are not sure why this is. If you encounter import errors related to NetworkX, go to the [GrinPy repository](https://github.com/somacdivad/grinpy) and clone it into the root directory. Then, take the folder "grinpy" from within that repository, extract it, and remove the rest.

## running the program

The general form for running these programs is 
```
python driver.py <size> <num> [--gtskip]
```
* <size> -- The size of the graphs to analyze. Choose between s (small), m (medium) and l (large).
* <num> -- The quantity of graphs to analyze. Must be between 1 and 1000.
* gtskip -- Optional; skips the ground truth calculations. Useful for medium and large graphs.

Here is an example command, which analyzes fifty medium graphs:
```
python driver.py m 50 --gtskip
```

The output of this graph will be two tables. The first table denotes one graph per row and the chromatic number determined by each algorithm (and the ground truth, if applicable). The second table denotes the distribution of chromatic numbers across all the graphs.