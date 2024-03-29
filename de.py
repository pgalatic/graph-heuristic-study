# author: Paul Galatic
#
# Graph heuristic study -- compute chi numbers
#
# inspired by:
# * https://ieeexplore.ieee.org/abstract/document/5952075\
# * https://ieeexplore.ieee.org/document/5365201

# standard lib
import sys
import copy
import math
import time
import random
import operator

# required lib
import numpy as np

# project lib
from solution import Solution
from greedy_color import greedy_color

TIME_FORMAT = '%H:%M:%S'

def log(s):
    '''More informative print debugging'''
    print('[%s]: %s' % (time.strftime(TIME_FORMAT, time.localtime()), str(s)))

class Particle(Solution):

    def __init__(self, graph, omega, phi):
        Solution.__init__(self, graph)
        self.omega = omega
        self.phi = phi

    def update(self, peers):
        x1 = peers[0].position
        x2 = peers[1].position
        x3 = peers[2].position
        # multiply x_diff by the mutation factor (omega) and add to x1
        donor = np.zeros(self.dimension)
        for idx in range(self.dimension):
            donor[idx] = x1[idx] + (self.omega * (x2[idx] - x3[idx]))
        idy = random.randrange(self.dimension)
        # apply crossover
        trial = np.zeros(self.dimension)
        for idx in range(self.dimension):
            chance = random.random()
            if chance <= self.phi or idx == idy:
                trial[idx] = donor[idx]
            else:
                trial[idx] = self.position[idx]
        # apply fitness function based on x vector
        trial_fitness = self.fit_func(trial)
        # only change if the trial candidate has a beter fitness score
        if trial_fitness > self.fitness:
            self.update_position(trial)

class Optimizer:

    def __init__(self, **kwargs):
        self.pops           = kwargs.get('pops', 50)
        self.generations    = kwargs.get('gens', 50)
        self.omega          = kwargs.get('omega', 0.5)
        self.phi            = kwargs.get('phi', 0.5)
        self.graph          = kwargs.get('graph', None)
        self.seed           = kwargs.get('seed', None)

        assert(self.graph)

        if self.seed:
            np.random.seed(self.seed)

        # instantiate a population of particles
        self.population = []
        for i in range(self.pops):
            self.population.append(Particle(self.graph, self.omega, self.phi))

    def step(self):
        # update every member of the population via its update function
        for pop in self.population:
            tmp_population = [item for item in self.population if item != pop]
            # updating requires 3 peers; select them randomly
            peers = random.sample(tmp_population, 3)
            pop.update(peers)
        # return the fittest member of the population
        self.population.sort(key=operator.attrgetter('fitness'), reverse=True)
        return self.population[0]

    def run(self):
        for t in range(self.generations):
            # log(f'Generation {t}...')
            gbest = self.step()
        return gbest
