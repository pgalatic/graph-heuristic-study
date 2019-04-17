# author: Paul Galatic
#
# Graph heuristic study -- compute chi numbers
#
# inspired by https://ieeexplore.ieee.org/abstract/document/5952075

# standard lib
import sys
import math
import copy
import random
import operator

# required lib
import numpy as np

# project lib
from greedy_color import greedy_color

class Solution:

    def __init__(self, graph):
        self.graph = graph
        self.position = np.random.rand(len(self.graph))
        self.fitness = self.fit_func()

    def get_order(self, position=None):
        '''
        The ordering is found by "collapsing" the position, which is given as a
        set of floats. The largest float is chosen first; ties are broken by
        taking the first index available (according to np.argmax()).
        '''
        if type(position) == type(None): position = self.position
        order = np.zeros(len(position))
        pos_copy = np.array(position) # don't want to alter self.position
        for idx in range(len(pos_copy)):
            maxi = np.argmax(pos_copy)
            order[idx] = maxi
            pos_copy[maxi] = -1 # set outside the domain
        return order

    def fit_func(self, position=None):
        '''
        Take the ratio of the minimum possible colors used to the colors found
        via greedy coloring + the particle's ordering. The "- 2" is to account
        for how a graph with > 1 node requires at least two colors (and we are
        not interested in graphs with 1 node.

        Returns a value of 0 if greedy_color() == len(graph) and 1 if
        greedy_color() == 2.
        '''
        order = self.get_order(position)
        return 1 - ((greedy_color(self.graph, order) - 2) / (len(self.graph) - 2))

    def check_position(self):
        '''Ensure the values of position stay within the domain [0-1].'''
        self.position[self.position > 1] = 1
        self.position[self.position < 0] = 0
