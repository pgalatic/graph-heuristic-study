# author: Paul Galatic
#
# Graph heuristic study -- compute chi numbers

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

def log(s):
    '''More informative print debugging'''
    print('[%s]: %s' % (time.strftime(TIME_FORMAT, time.localtime()), str(s)))

class Particle:

    def __init__(self, graph, omega, phi):        
        self.omega = omega
        self.phi = phi
        self.graph = graph
        self.position = np.random.rand(len(self.graph))
        self.fitness = self.fit_func()
    
    def update(self, peers):
        x1 = peers[0].position
        x2 = peers[1].position
        x3 = peers[2].position
        # multiply x_diff by the mutation factor (omega) and add to x1
        donor = np.zeros(len(self.position))
        for idx in range(len(self.position)):
            donor[idx] = x1[idx] + (self.omega * (x2[idx] - x3[idx]))
        idy = random.randrange(len(self.position))
        # apply crossover
        trial = np.zeros(len(self.position))
        for idx in range(len(self.position)):
            chance = random.random()
            if chance <= self.phi or idx == idy:
                trial[idx] = donor[idx]
            else:
                trial[idx] = self.position[idx]
        trial_fitness = self.fit_func(trial)
        if trial_fitness > self.fitness:
            self.position = trial
            self.check_position()
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

class DE_Opt:

    def __init__(self, **kwargs):
        self.pops           = kwargs.get('pops', 50)
        self.generations    = kwargs.get('gens', 100)
        self.omega          = kwargs.get('omega', 0.5)
        self.phi            = kwargs.get('phi', 0.5)
        self.graph          = kwargs.get('graph', None)
        self.seed           = kwargs.get('seed', None)
        
        assert(self.graph)
        
        if self.seed:
            np.random.seed(self.seed)
        
        self.population = []
        for i in range(self.pops):
            self.population.append(Particle(self.graph, self.omega, self.phi))

    def step(self):
        for pop in self.population:
            tmp_population = [item for item in self.population if item != pop]
            peers = random.sample(tmp_population, 3)
            pop.update(peers)
        self.population.sort(key=operator.attrgetter('fitness'), reverse=True)
        return self.population[0]

    def run(self):
        for t in range(self.generations):
            gbest = self.step()
        return gbest

def compute_chi(graphs):
    '''
    Computes the set of best found chi numbers for a given graph
    '''
    results = dict()
    for graph in graphs:
        de_opt = DE_Opt(graph=graph)
        gbest = de_opt.run()
        results[graph] = greedy_color(graph, gbest.get_order(gbest.position))
    return results
        