# author: Paul Galatic
#
# Program to

# STD LIB
import os
import copy
import time
import random
import argparse
import linecache
from pathlib import Path

# REQUIRED LIB
import numpy as np
import grinpy as gp
import networkx as nx
import tabulate as tab

# PROJECT LIB
import de as de
import pso as pso
# import aco as aco
from greedy_color import greedy_color

# CONSTANTS
TIME_FORMAT = '%H:%M:%S'
GRAPH_DIR = Path('graph/')

SML = 10
MED = 23
LRG = 300
NUM = 1000

SML_NAME = f'n{SML}.g6'
MED_NAME = f'n{MED}.g6'
LRG_NAME = f'n{LRG}.g6'

def log(s):
    '''More informative print debugging'''
    print('[%s]: %s' % (time.strftime(TIME_FORMAT, time.localtime()), str(s)))

def parse_args():
    '''Parses arguments'''
    ap = argparse.ArgumentParser()

    ap.add_argument('mode', type=str,
        help='[s|m|l] -- small, medium, or large')
    ap.add_argument('n', type=int,
        help='the number of graphs to analyze')
    ap.add_argument('--gtskip', action='store_true',
        help='set true to skip ground truth calculations')
    return ap.parse_args()

def gen_rand_graphs(dim, theta=0.85):
    '''Generates random graphs based on parameter theta'''
    graphs = []
    
    log(f'generating {NUM} Erdős-Rényi graphs of size {dim}...')
    for _ in range(NUM):
        # create a blank adjacency matrix
        graph = np.zeros(shape=(dim, dim))

        # add edges according to a random process
        for idx in range(dim - 1):
            for idy in range(idx + 1, dim - 1):
                rand = random.random()
                if rand <= theta:
                    # make sure the graphs are symmetrical
                    graph[idx][idy] = 1
                    graph[idy][idx] = 1
        graphs.append(graph)

    return [nx.from_numpy_array(graph) for graph in graphs]

def record_graphs(graphs, path):
    '''writes graphs in g6 format to the designated filename'''
    for graph in graphs:
        with open('temp', 'w') as temp:
            nx.write_graph6(graph, 'temp', header=False)
        with open('temp', 'r') as temp:
            with open(path, 'a') as out:
                out.write(''.join(temp.readlines()))

    with open(path, 'r') as f:
        log('Recorded %d graphs' % len(f.readlines()))

    os.remove('temp')

def load_graphs(mode, num):
    '''
    Loads a random sample of graphs from the graphs file. Returns a mapping of
    the graph to its chromatic number.
    '''
    log('loading graphs...')

    if 's' in mode:
        fname = str(GRAPH_DIR / SML_NAME)
    elif 'm' in mode:
        fname = str(GRAPH_DIR / MED_NAME)
    elif 'l' in mode:
        fname = str(GRAPH_DIR / LRG_NAME)
    else:
        raise Exception(f'Could not recognize mode: {mode}.')

    with open(fname, 'r', newline='\n', encoding='ISO-8859-1') as f:
        length = sum(1 for _ in f)

    if num >= length:
        num = length - 1
        log(f'WARNING: Can only load up to {length} graphs from this file.')

    with open(fname, 'r') as f:
        lines = f.readlines()
    raw_graphs = random.sample(lines, num)

    # create temporary file so that nx can read it
    temp_path = 'temp'
    with open(temp_path, 'w', newline='\n') as f:
        f.writelines(raw_graphs)

    graphs = nx.read_graph6(temp_path)
    os.remove(temp_path)

    log(f'...{len(graphs)} graphs loaded.')

    return graphs

def compute_chi(optim_module, graphs):
    '''
    Computes the set of best found chi numbers for a given graph
    '''
    results = dict()
    for graph in graphs:
        gbest = optim_module.Optimizer(graph=graph).run()
        results[graph] = greedy_color(graph, gbest.get_order(gbest.position))
    return results

def main():
    '''Driver program'''
    args = parse_args()
    log('Starting...')

    # load graphs, or generate them if they don't exist
    if not os.path.exists(str(GRAPH_DIR / SML_NAME)):
        record_graphs(gen_rand_graphs(SML), str(GRAPH_DIR / SML_NAME))
    if not os.path.exists(str(GRAPH_DIR / MED_NAME)):
        record_graphs(gen_rand_graphs(MED), str(GRAPH_DIR / MED_NAME))
    if not os.path.exists(str(GRAPH_DIR / LRG_NAME)):
        record_graphs(gen_rand_graphs(LRG), str(GRAPH_DIR / LRG_NAME))
    graphs = load_graphs(args.mode, args.n)

    # ground truth graphs
    
    start = time.time()
    if args.gtskip:
        gt_graphs = {graph: None for graph in graphs} 
    else:
        log('Calculating ground truth...')
        gt_graphs = {graph : gp.chromatic_number(graph) for graph in graphs}
        log(f'{round(time.time() - start, 3)} seconds')

    # color each graph with each algorithm
    # each algorithm will predict the chi of the graph and this will form new
    # mappings of graph -> chi
    log('Calculating greedy colorings...')
    start = time.time()
    gr_graphs = {graph: greedy_color(graph) for graph in graphs}
    log(f'{round(time.time() - start, 3)} seconds')

    log('Calculating differential evolution colorings...')
    start = time.time()
    de_graphs = compute_chi(de, graphs)
    log(f'{round(time.time() - start, 3)} seconds')

    log('Calculating particle swarm optimization colorings...')
    start = time.time()
    pso_graphs = compute_chi(pso, graphs)
    log(f'{round(time.time() - start, 3)} seconds')

    # analyze the difference between the predictions and the actual
    table_1 = tab.tabulate(
        zip(list(range(len(graphs))), gt_graphs.values(), gr_graphs.values(), de_graphs.values(), pso_graphs.values()), 
        headers=['num', 'truth', 'greedy', 'de', 'pso'] )
    # log(f'\nChromatic numbers for graphs:\n{table_1}')
    min_chi = min([min(gr_graphs.values()), min(de_graphs.values())])
    max_chi = max([max(gr_graphs.values()), max(de_graphs.values())])
    gr_modes = [list(gr_graphs.values()).count(idx) for idx in range(min_chi, max_chi + 1)]
    de_modes = [list(de_graphs.values()).count(idx) for idx in range(min_chi, max_chi + 1)]
    pso_modes = [list(pso_graphs.values()).count(idx) for idx in range(min_chi, max_chi + 1)]
    table_2 = tab.tabulate(
        zip(list(range(min_chi, max_chi + 1)), gr_modes, de_modes, pso_modes),
        headers=['num', 'greedy', 'de', 'pso']
    )
    log(f'\nFrequency of chromatic numbers:\n{table_2}')


    log('...finished.')
    return 0

if __name__ == '__main__':
    main()
