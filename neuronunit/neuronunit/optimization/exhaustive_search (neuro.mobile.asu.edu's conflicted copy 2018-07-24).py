
#from neuronunit.optimization import get_neab
#tests = get_neab.tests
import pdb

import multiprocessing
from collections import OrderedDict

from neuronunit.optimization.model_parameters import model_params
from neuronunit.optimization import model_parameters as modelp
from neuronunit.optimization import data_transport_container
from neuronunit.optimization.optimization_management import nunit_evaluation, update_deap_pop
from neuronunit.optimization.optimization_management import update_dtc_pop
import numpy as np
from collections import OrderedDict

import copy
from copy import deepcopy
import math

import dask.bag as db
from sklearn.grid_search import ParameterGrid
import scipy

import pickle
import os
import numpy as np
npartitions = multiprocessing.cpu_count()
npart = multiprocessing.cpu_count()

import os


class WSListIndividual(list):
    """Individual consisting of list with weighted sum field"""
    def __init__(self, *args, **kwargs):
        """Constructor"""
        self.rheobase = None
        self.dtc = None

        super(WSListIndividual, self).__init__(*args, **kwargs)



def reduce_params(model_params,nparams):
    key_list = list(model_params.keys())
    reduced_key_list = key_list[0:nparams]
    subset = { k:model_params[k] for k in reduced_key_list }
    return subset


def chunks(l, n):
    # For item i in a range that is a length of l,
    ch = []
    for i in range(0, len(l), n):
        # Create an index range for l of n items:
        ch.append(l[:][i:i+n])
    return ch

def build_chunk_grid(npoints, provided_keys):
    grid_points, maps = create_grid(npoints = npoints, provided_keys = provided_keys)
    temp = OrderedDict(grid_points[0]).keys()
    tds = list(temp)
    pops = []
    for g in grid_points:
        pre_pop = list(g.values())
        pop = WSListIndividual(pre_pop)
        pops.append(pop)

    # divide population into chunks that reflect the number of CPUs.
    # don't want lists of lengths 1 that are awkward to iterate over.
    # so check if there would be a chunk of list length 1, and if so divide by a different numberself.
    # that is still dependant on CPU number.
    if len(pops) % npartitions != 1:
        pops_ = chunks(pops,npartitions)
    else:

        pops_ = chunks(pops,npartitions-2)
    try:
        assert pops_[0] != pops_[1]
    except:
        pdb.set_trace()
    return pops_, tds


def sample_points(iter_dict, npoints=3):
    replacement = {}
    for p in range(0,len(iter_dict)):
        k,v = iter_dict.popitem(last=False)
        sample_points = list(np.linspace(v.max(),v.min(),npoints))
        replacement[k] = sample_points
    return replacement

'''depreciated
def create_refined_grid(best_point,point1,point2):

    # Can be used for creating a second pass fine grained grid

    # This function reports on the deltas brute force obtained versus the GA found attributes.
    #from neuronunit.optimization import model_parameters as modelp
    #mp = modelp.model_params
    new_search_interval = {}
    for k,v in point1.attrs.items():
        higher =  max(float(point1.attrs[k]),float(v), point2.attrs[k])
        lower = min(float(point1.attrs[k]),float(v), point2.attrs[k])
        temp = list(np.linspace(lower,higher,10))
        new_search_interval[k] = temp[1:-2] # take only the middle two points
        # discard edge points, as they are already well searched/represented.
    grid = list(ParameterGrid(new_search_interval))
    return grid
'''

def update_dtc_grid(item_of_iter_list):

    dtc = data_transport_container.DataTC()
    dtc.attrs = deepcopy(item_of_iter_list)
    dtc.scores = {}
    dtc.rheobase = None
    dtc.evaluated = False
    dtc.backend = 'NEURON'
    return dtc

def create_a_map(subset):
    maps = {}
    for k,v in subset.items():
        maps[k] = {}
        for ind,j in enumerate(subset[k]):
            maps[k][j] = ind
    return maps


def create_grid(npoints=3,nparams=7,provided_keys=None,ga=None):
    '''
    Description, create a grid of evenly spaced samples in model parameters to search over.
    Inputs: npoints, type: Integer: number of sample points per parameter
    nparams, type: Integer: number of parameters to use, conflicts, with next argument.
    nparams, iterates through a list of parameters, and assigns the nparams to use via stupid counting.
    provided keys: explicitly define state the model parameters that are used to create the grid of samples, by
    keying into an existing of parameters.

    This method needs the user of the method to declare a dictionary of model parameters in a path:
    neuronunit.optimization.model_parameters.

    Miscallenous, once grid created by this function
    has been evaluated using neuronunit it can be used for informing a more refined second pass fine grained grid
    '''
    mp = OrderedDict(modelp.model_params)
    # smaller is a dictionary thats not necessarily as big
    # as the grid defined in the model_params file. Its not necessarily
    # a smaller dictionary, if it is smaller it is reduced by reducing sampling
    # points.
    smaller = {}
    smaller = OrderedDict(sample_points(mp, npoints=npoints))
    if type(provided_keys) is type(None):
        key_list = list(smaller.keys())
        reduced_key_list = key_list[0:nparams]
    else:
        reduced_key_list = list(provided_keys)

    # subset is reduced, by reducing parameter keys.
    subset = OrderedDict( {k:smaller[k] for k in reduced_key_list})

    maps = create_a_map(subset)
    if type(ga) is not None:

        if npoints > 1:
            for k,v in subset.items():
                v[0] = v[0]*1.0/3.0
                v[1] = v[1]*2.0/3.0

    # The function of maps is to map floating point sample spaces onto a  monochromataic matrix indicies.
    grid = list(ParameterGrid(subset))
    return grid, maps

def tfg2i(x, y, z):
    '''
    translate_float_grid_to_index
    Takes x, y, z values as lists and returns a 2D numpy array
    '''
    dx = abs(np.sort(list(set(x)))[1] - np.sort(list(set(x)))[0])
    dy = abs(np.sort(list(set(y)))[1] - np.sort(list(set(y)))[0])
    i = ((x - min(x)) / dx).astype(int) # Longitudes
    j = ((y - max(y)) / dy).astype(int) # Latitudes
    grid = np.nan * np.empty((len(set(j)),len(set(i))))
    grid[j, i] = z # if using latitude and longitude (for WGS/West)
    return grid

def tfc2i(x, y, z,err):
    '''
    translate_float_cube_to_index

    Takes x, y, z values as lists and returns a 2D numpy array
    '''
    dx = abs(np.sort(list(set(x)))[1] - np.sort(list(set(x)))[0])
    dy = abs(np.sort(list(set(y)))[1] - np.sort(list(set(y)))[0])
    dz = abs(np.sort(list(set(z)))[1] - np.sort(list(set(y)))[0])

    i = ((x - min(x)) / dx).astype(int) # Longitudes
    j = ((y - max(y)) / dy).astype(int) # Latitudes
    k = ((z - max(z)) / dz).astype(int) # Latitudes

    grid = np.nan * np.empty((len(set(i)),len(set(j)), len(set(k)) ))
    print(len(set(i)),len(set(j)), len(set(k)) )
    print(np.shape(grid))
    grid[i,j,k] = err # if using latitude and longitude (for WGS/West)
    return



def transdict(dictionaries):
    from collections import OrderedDict
    mps = OrderedDict()
    sk = sorted(list(dictionaries.keys()))
    for k in sk:
        mps[k] = dictionaries[k]
    return mps

def run_grid(nparams,npoints,tests,provided_keys = None, hold_constant = None):
    consumable_ ,td = build_chunk_grid(npoints,nparams,provided_keys)
    if type(hold_constant) is not type(None):
        hc = list(hold_constant.values())[0]
        for c in consumable_:
            for i in c:
                i.append(hc)
        td.append(list(hold_constant.keys())[0])
    cnt = 0
    grid_results = []
    consumable = iter(consumable_)
    for sub_pop in consumable:
        grid_results.extend(update_deap_pop(sub_pop, tests, td))
        #assert len(grid_results[0].dtc.attrs.keys()) == 3
        assert len(grid_results[0].dtc.scores.keys()) >= 2

        with open('grid_cell_results'+str(nparams)+str('.p'),'wb') as f:
            pickle.dump(grid_results,f)
        with open('iterator_state'+str(nparams)+str('.p'),'wb') as f:
            pickle.dump([sub_pop, tests, cnt],f)
        cnt += 1
        print('done_block_of_N_cells: ',cnt)
    return grid_results
