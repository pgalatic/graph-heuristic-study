# author: Paul Galatic
#
# Program to

# STD LIB
import os
import time
import random
import argparse
import linecache
import subprocess
from pathlib import Path

# REQUIRED LIB
import grinpy as gp
import networkx as nx

# PROJECT LIB

# CONSTANTS
TIME_FORMAT = '%H:%M:%S'
GRAPH_DIR = Path('graph/')
GRAPHS_NAME = 'n10.g6'

def log(s):
    '''More informative print debugging'''
    print('[%s]: %s' % (time.strftime(TIME_FORMAT, time.localtime()), str(s)))

def parse_args():
    '''Parses arguments'''
    ap = argparse.ArgumentParser()
    
    ap.add_argument('-n', required=True,
        help='the number of graphs to analyze')
    ap.add_argument('--shell', action='store_true',
        help='set to True if running on a Windows environment')
    
    return ap.parse_args()

def gen_graphs(shell):
    '''Generates graphs and puts them in the GRAPHS directory'''
    log('generating graphs...')
    if shell:
        raise Exception('Operation not supported on Windows.')
    
    path_in = str(GRAPH_DIR) + '/geng'
    path_out = str(GRAPH_DIR / GRAPHS_NAME)
    subprocess.call([f'./{path_in}', '10', '>', f'{path_out}'])
    
    with open(path_out, 'r+', newline='\n', encoding='ISO-8859-1') as f:
        content = f.read()
        f.seek(0, 0)
        f.write('# coding: iso-8859-1'.rstrip('\r\n') + '\n' + content)

def load_graphs(num):
    '''
    Loads a random sample of graphs from the graphs file. Returns a mapping of
    the graph to its chromatic number.
    '''
    log('loading graphs...')
    
    fname = str(GRAPH_DIR / GRAPHS_NAME)
    temp_path = 'temp'
    
    with open(fname, 'r', newline='\n', encoding='ISO-8859-1') as f:
        length = sum(1 for _ in f)
    
    idxs = random.sample(range(length), int(num))
    raw_graphs = [linecache.getline(fname, idx) for idx in idxs]
    
    # create temporary file so that nx can read it
    with open(temp_path, 'w', newline='\n') as f:
        f.writelines(raw_graphs)
    
    graphs = nx.read_graph6(temp_path)
    os.remove(temp_path)
    
    return {graph : gp.chromatic_number(graph) for graph in graphs}

def main():
    '''Driver program'''
    args = parse_args()
    log('Starting...')

    # load graphs
    if not os.path.exists(str(GRAPH_DIR / GRAPHS_NAME)):
        gen_graphs(args.shell)
    graphs_with_chi = load_graphs(args.n)
    graphs = graphs_with_chi.keys()
    
    # log(graphs_with_chi)
    
    # color each graph with each algorithm
    # each algorithm will predict the chi of the graph and this will form new
    # mappings of graph -> chi
    
    # TODO
    
    # analyze the difference between the predictions and the actual
    
    # TODO
    
    log('...finished.')
    return 0

if __name__ == '__main__':
    main()