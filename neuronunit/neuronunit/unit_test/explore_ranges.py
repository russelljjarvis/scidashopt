import pickle
import copy
import os

from neuronunit.tests import np, pq, cap, VmTest, scores, AMPL, DELAY, DURATION
from neuronunit.optimization import get_neab
from neuronunit.optimization.optimization_management import run_ga
from neuronunit.models.NeuroML2 import model_parameters as modelp
from neuronunit.models.NeuroML2 .model_parameters import path_params

from neuronunit.tests import np, pq, cap, VmTest, scores, AMPL, DELAY, DURATION

import matplotlib as mpl
mpl.use('Agg')
from matplotlib.colors import LogNorm
from neuronunit.optimization.exhaustive_search import run_grid, reduce_params, create_grid, WSListIndividual
import matplotlib.pyplot as plt

from neuronunit import plottools
plot_surface = plottools.plot_surface
scatter_surface = plottools.plot_surface

electro_path = str(os.getcwd())+'/pipe_tests.p'
print(os.getcwd())
assert os.path.isfile(electro_path) == True
with open(electro_path,'rb') as f:
    electro_tests = pickle.load(f)

from neuronunit.optimization import exhaustive_search as es
import quantities as pq

from itertools import product
import matplotlib.pyplot as plt


def get_tests():
    from neuronunit.optimization import get_neab
    electro_path = str(os.getcwd())+'/pipe_tests.p'
    assert os.path.isfile(electro_path) == True
    with open(electro_path,'rb') as f:
        electro_tests = pickle.load(f)
    test, observation = electro_tests[0]
    tests = copy.copy(electro_tests[0][0])
    tests_ = []
    tests_ += [tests[0]]
    tests_ += tests[4:7]
    return tests_, test, observation

tests_,test, observation = get_tests()

ax = None

from numba import jit

#@jit
def check_line(line,gr,newrange,key):
    # Is this a concave down shape (optima in the middle)
    # Or is the most negative value on an edge?
    # if it's on the edge calculate a new parameter value to explore
    range_adj = False
    min_ = np.min(line)
    cl = [ g.dtc.attrs[key] for g in gr ]
    new = None
    if line[0] == min_:
        attrs = gr[0].dtc.attrs[key]
        remin = - 2*np.abs(attrs)*2
        cl.insert(0,remin)
        newrange[key] = cl
        range_adj = True
        new_param_val = remin
    if line[-1] == min_:
        attrs = gr[-1].dtc.attrs[key]
        remax = np.abs(attrs)*2
        cl.append(remax)
        newrange[key] = cl
        range_adj = True
        new_param_val = remax

    return (newrange, range_adj, new_param_val)

def mp_process(newrange):
    from neuronunit.models.NeuroML2 import model_parameters as modelp
    mp = copy.copy(modelp.model_params)
    for k,v in newrange.items():
        if type(v) is not type(None):
            mp[k] = (np.min(v),np.max(v))
    return mp

from neuronunit.models.NeuroML2 import model_parameters as modelp
from neuronunit.optimization.optimization_management import nunit_evaluation, update_deap_pop
from collections import OrderedDict

# https://stackoverflow.com/questions/33467738/numba-cell-vars-are-not-supported
# numba jit does not work on nested list iteration
#@jit
def pre_run(tests,opt_keys):
    # algorithmically find the the edges of parameter ranges, via a course grained
    # sampling of extreme parameter values
    # to find solvable instances of Izhi-model, (models with a rheobase value).
    nparams = len(opt_keys)
    from neuronunit.models.NeuroML2 import model_parameters as modelp
    mp = copy.copy(modelp.model_params)

    cnt = 0
    fc = {} # final container
    for key in opt_keys:
        print(key,mp)
        gr = run_grid(3,tests,provided_keys = key, mp_in = mp)
        line = [ g.dtc.get_ss() for g in gr]
        nr = {key:None}
        newrange, range_adj, new = check_line(line,gr,nr,key)
        cnt = 0
        while range_adj == True:
            # while the sampled line is not concave (when minimas are at the edges)
            # sample a point to a greater extreme
            mp = mp_process(newrange)
            gr_ = update_deap_pop(new, tests, key)
            param_line = [ g.dtc.attrs[key] for g in gr ]

            # take the new sample 'gr_' and insert it to the start or end of the list
            # appropriately obeying item order:
            # start smaller values, end larger values.
            less = bool(new < np.min(param_line))
            if less:
                gr.insert(0,gr_)
            else:
                gr.append(gr_)

            # make a line out of the sum of error components.
            line = [ g.dtc.get_ss() for g in gr]
            newrange, range_adj, new = check_line(line,gr,newrange,key)
            mp = mp_process(newrange)
            cnt += 1

        fc[key] = {}
        fc[key]['line'] = line
        fc[key]['range'] = newrange
        fc[key]['cnt'] = cnt
    return fc, mp
