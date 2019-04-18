# author: Paul Galatic
#
# Program to

# STD LIB
import time
import argparse

# REQUIRED LIB

# PROJECT LIB

# CONSTANTS
TIME_FORMAT = '%H:%M:%S'

def log(*args):
    '''More informative print debugging'''
    t = time.strftime(TIME_FORMAT, time.localtime())
    s = ' '.join([str(arg) for arg in args])
    print(f'[{t}]: {s}')

def greedy_color(graph, order=None):
    '''
    Each vertex is processed in order and is assigned the first available color
    (i.e. added to the first available set that does not contain its 
    neighbors).
    '''
    color_class = list()
    
    # if there is no ordering use the default order
    if type(order) == type(None): order = list(range(len(graph)))
    
    # label the nodes in order
    for idx in order:
        # start with the first color, but assume it won't work
        curr_color = 0
        valid = False
        
        # loop until we have a valid configuration
        while not valid:
            # if our current color isn't present in keys, that means we've 
            # exceeded the current color range and need to initialize a new set
            if curr_color == len(color_class):
                color_class.append(list())
                # we'll always be able to fit into this new set
                valid = True
                break
            
            # look if any neighbors are present in this coloration
            neighbor_present = False
            for neighbor in graph.neighbors(idx):
                if neighbor in color_class[curr_color]:
                    neighbor_present = True
                    break
            # if a neighbor is in this color class, then we have to move to the
            # next one
            if neighbor_present: curr_color += 1
            else: valid = True
        
        # now that we've found a valid color, we can add it to the class
        color_class[curr_color].append(idx)

    return len(color_class)

