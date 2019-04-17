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
from solution import Solution
from greedy_color import greedy_color

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

class Optimizer:

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
