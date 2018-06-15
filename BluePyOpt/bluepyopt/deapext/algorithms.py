"""Optimisation class
Copyright (c) 2016, EPFL/Blue Brain Project

 This file is part of BluePyOpt <https://github.com/BlueBrain/BluePyOpt>

 This library is free software; you can redistribute it and/or modify it under
 the terms of the GNU Lesser General Public License version 3.0 as published
 by the Free Software Foundation.

 This library is distributed in the hope that it will be useful, but WITHOUT
 ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
 FOR A PARTICULAR PURPOSE.  See the GNU Lesser General Public License for more
 details.

 You should have received a copy of the GNU Lesser General Public License
 along with this library; if not, write to the Free Software Foundation, Inc.,
 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
"""

# pylint: disable=R0914, R0912


import random
import logging

import deap.algorithms
import deap.tools
import pickle
import numpy

import copy
from neuronunit.optimization import optimization_management as om

import pdb

logger = logging.getLogger('__main__')


def _evaluate_invalid_fitness(toolbox, population):
    '''Evaluate the individuals with an invalid fitness

    Returns the count of individuals with invalid fitness
    '''
    invalid_ind = [ind for ind in population if not ind.fitness.valid]
    fitnesses = toolbox.evaluate(invalid_ind)
    # package
    for ind, fit in zip(invalid_ind, fitnesses):
        ind.fitness.values = fit
    return len(invalid_ind)


def _update_history_and_hof(halloffame, history, population,td):
    '''Update the hall of fame with the generated individuals

    Note: History and Hall-of-Fame behave like dictionaries
    '''

    if halloffame is not None:
        halloffame.update(population)
    history.update(population)
    for h in halloffame:
        print(bool(hasattr(h,'dtc')))
        print(bool(hasattr(h.dtc,'score')))

        #assert hasattr(h,'dtc')
        #assert hasattr(h.dtc,'score')


def _record_stats(stats, logbook, gen, population, invalid_count):
    '''Update the statistics with the new population'''
    record = stats.compile(population) if stats is not None else {}
    logbook.record(gen=gen, nevals=invalid_count, **record)


def _get_offspring(parents, toolbox, cxpb, mutpb):
    '''return the offsprint, use toolbox.variate if possible'''
    if hasattr(toolbox, 'variate'):
        return toolbox.variate(parents, toolbox, cxpb, mutpb)
    return deap.algorithms.varAnd(parents, toolbox, cxpb, mutpb)


def _get_elite(halloffame, nelite):
    if nelite > 0 and halloffame is not None:
        normsorted_idx = numpy.argsort([ind.fitness.norm for ind in halloffame])
        # Return nelite best individuals
        return [halloffame[idx] for idx in normsorted_idx[:nelite]]
    return list()

from . import tools
import numpy as np

def eaAlphaMuPlusLambdaCheckpoint(
        population,
        toolbox,
        mu,
        cxpb,
        mutpb,
        ngen,
        stats = None,
        halloffame = None,
        nelite = 0,
        cp_frequency = 1,
        cp_filename = None,
        continue_cp = False,
        selection = 'selIBEA',
        td=None):

    if continue_cp:
        # A file name has been given, then load the data from the file
        cp = pickle.load(open(cp_filename, "r"))
        population = cp["population"]
        parents = cp["parents"]
        start_gen = cp["generation"]
        halloffame = cp["halloffame"]
        logbook = cp["logbook"]
        history = cp["history"]
        random.setstate(cp["rndstate"])
    else:
        # Start a new evolution
        start_gen = 1
        parents = population[:]
        logbook = deap.tools.Logbook()
        logbook.header = ['gen', 'nevals'] + (stats.fields if stats else [])
        history = deap.tools.History()

        # TODO this first loop should be not be repeated !
        invalid_count = _evaluate_invalid_fitness(toolbox, population)
        gen_vs_hof = []
        _update_history_and_hof(halloffame, history, population, td)

        gen_vs_hof.append(halloffame)
        _record_stats(stats, logbook, start_gen, population, invalid_count)
    # Begin the generational process
    for gen in range(start_gen + 1, ngen + 1):
        offspring = _get_offspring(parents, toolbox, cxpb, mutpb)
        population = parents + offspring

        invalid_count = _evaluate_invalid_fitness(toolbox, offspring)

        breeder_fit = np.mean([p.fitness.values for p in parents])
        regular_pop_fit = [p.fitness.values for p in population]
        offspring_fit = np.mean([p.fitness.values for p in offspring])
        assert np.min(regular_pop_fit) > np.min(breeder_fit)
        assert np.mean(regular_pop_fit) > np.mean(breeder_fit)
        for p in population:
            assert hasattr(p,'dtc')
            assert hasattr(p.dtc,'score')

        _update_history_and_hof(halloffame, history, population, td)
        gen_vs_hof.append(halloffame[-1])


        _record_stats(stats, logbook, gen, population, invalid_count)
        #import deap.tools
        # Select the next generation parents
        toolbox.register("select", tools.selIBEA)
        parents = toolbox.select(population + _get_elite(halloffame, nelite), mu)
        print('compare parents to population fitness here')
        breeder_fit = [p.fitness.values for p in parents]
        regular_pop_fit = [p.fitness.values for p in population]
        assert np.min(regular_pop_fit) > np.min(breeder_fit)
        assert np.mean(regular_pop_fit) > np.mean(breeder_fit)
        logger.info(logbook.stream)

        if(cp_filename):# and cp_frequency and
           #gen % cp_frequency == 0):
            cp = dict(population=population,
                      generation=gen,
                      parents=parents,
                      halloffame=halloffame,
                      history=history,
                      logbook=logbook,
                      rndstate=random.getstate())
            pickle.dump(cp, open(cp_filename, "wb"))
            print('Wrote checkpoint to %s', cp_filename)
            logger.debug('Wrote checkpoint to %s', cp_filename)

    return population, logbook, history, gen_vs_hof
