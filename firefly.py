# author: Zhizhuo Yang
#
# Graph coloring using firefly algorithm
#
# reference: https://arxiv.org/pdf/1003.1466.pdf


import numpy as np
from numpy import linalg as LA
import random
import operator

# project lib
from solution import Solution


class Firefly(Solution):
    def __init__(self, graph, alpha, beta, gamma):
        Solution.__init__(self, graph)
        self.alpha = alpha        # control of randomness
        self.beta = beta          # attractiveness
        self.gamma = gamma        # light absorption coefficient
        self.intensity = None     # Intensity of individual firefly


    def move_firefly(self, j_position):
        # Cartesian distance
        dist = LA.norm(self.position - j_position)
        # update position
        pos_new = self.position + self.beta*np.exp(-self.gamma*dist**2) * (j_position-self.position) + \
            self.alpha * (random.uniform(0, 1)-0.5)
        self.update_position(pos_new)

    def update_intensity(self, obj_func):
        self.intensity = obj_func(self.position)

class Optimizer:
    def __init__(self, **kwargs):
        self.population_size = int(kwargs.get('pops', 50))
        self.generations = kwargs.get('gens', 50)
        self.gamma = kwargs.get('gamma', 0.97)  # absorption coefficient
        self.alpha = kwargs.get('alpha', 0.25)  # randomness [0,1]
        self.beta_0 = kwargs.get('beta_0', 1)   # attractiveness at distance=0
        self.best = None
        self.graph = kwargs.get('graph', None)

        assert self.graph

        self.seed = kwargs.get('seed', None)
        if self.seed:
            np.random.seed(self.seed)
        self.population = [Firefly(self.graph, self.alpha, self.beta_0, self.gamma)
                           for _ in range(self.population_size)]
        # calculate initial intensity
        for firefly in self.population:
            firefly.fitness = firefly.fit_func(firefly.position)

    def step(self):
        # rank the solutions
        self.population.sort(key=operator.attrgetter('fitness'), reverse=True)
        # compare each pair of fireflies and move them accordingly
        for i in self.population:
            for j in self.population:
                if j.fitness > i.fitness:
                    i.move_firefly(j.position)

        # update the best solution
        if not self.best or self.population[0].fitness > self.best:
            self.best = self.population[0].fitness
        return self.population[0]

    def run(self):
        for t in range(self.generations):
            # log(f'Generation {t}...')
            gbest = self.step()
        return gbest