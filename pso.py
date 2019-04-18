# author: Ari Zerner
#
# Graph heuristic study -- particle swarm optimization
#
# https://en.wikipedia.org/wiki/Particle_swarm_optimization

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

class Particle(Solution):

    def __init__(self, graph, omega, phi_particle, phi_global):
        Solution.__init__(self, graph)
        self.omega         = omega
        self.phi_particle  = phi_particle
        self.phi_global    = phi_global
        self.velocity      = np.random.rand(self.dimension) * 2 - 1
        self.best_position = self.position
        self.best_fitness  = self.fitness

    def update(self, global_best_position):
        r_p = np.random.rand(self.dimension)
        r_g = np.random.rand(self.dimension)
        self.velocity = ( self.omega * self.velocity
                        + self.phi_particle * r_p * (self.best_position - self.position)
                        + self.phi_global * r_g * (global_best_position - self.position))
        self.update_position(self.position + self.velocity)
        if self.fitness > self.best_fitness:
            self.best_position = self.position
            self.best_fitness = self.fitness

class Optimizer:

    def __init__(self, **kwargs):
        self.pops          = kwargs.get('pops', 50)
        self.generations   = kwargs.get('gens', 50)
        self.omega         = kwargs.get('omega', 0.5)
        self.phi_particle  = kwargs.get('phi_particle', 0.5)
        self.phi_global    = kwargs.get('phi_global', 0.5)
        self.graph         = kwargs.get('graph', None)
        self.seed          = kwargs.get('seed', None)
        self.best_position = None
        self.best_fitness  = None

        assert(self.graph)

        if self.seed:
            np.random.seed(self.seed)

        self.population = []
        for i in range(self.pops):
            pop = Particle(self.graph, self.omega, self.phi_particle, self.phi_global)
            self.population.append(pop)
            if (self.best_fitness is None) or (pop.fitness > self.best_fitness):
                self.best_position = pop.position
                self.best_fitness = pop.fitness

    def step(self):
        for pop in self.population:
            pop.update(self.best_position)
            if pop.fitness > self.best_fitness:
                self.best_position = pop.position
                self.best_fitness = pop.fitness
        self.population.sort(key=operator.attrgetter('fitness'), reverse=True)
        return self.population[0]

    def run(self):
        for t in range(self.generations):
            gbest = self.step()
        return gbest
