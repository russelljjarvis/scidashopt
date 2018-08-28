
import numpy as np
import matplotlib
matplotlib.use('Agg')

import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
import math as math
from pylab import rcParams
from neuronunit.optimization.optimization_management import run_ga
from neuronunit.optimization.exhaustive_search import run_grid, reduce_params, create_grid
from neuronunit.optimization.model_parameters import model_params


import os
import pickle
from neuronunit.optimization import get_neab
from neuronunit.optimization.results_analysis import min_max, error_domination, param_distance


from neuronunit.optimization.results_analysis import make_report
import copy
reports = {}
npoints = 10


electro_path = str(os.getcwd())+'/pipe_tests.p'
print(os.getcwd())
assert os.path.isfile(electro_path) == True
with open(electro_path,'rb') as f:
    electro_tests = pickle.load(f)
<<<<<<< HEAD

electro_tests = get_neab.replace_zero_std(electro_tests)
electro_tests = get_neab.substitute_parallel_for_serial(electro_tests)
test, observation = electro_tests[0]


# for nparams in range(1,3):
#    pass
# nparams = 2
# tests = copy.copy(electro_tests[0][0][0:2])
=======

electro_tests = get_neab.replace_zero_std(electro_tests)
electro_tests = get_neab.substitute_parallel_for_serial(electro_tests)
test, observation = electro_tests[0]


nparams = 2
tests = copy.copy(electro_tests[0][0][0:2])


#with open('pre_grid_reports.p','rb') as f:
#    [grid_results,nparams] = pickle.load(f)
>>>>>>> 13fe3fde8c76de2d719acdf82b3a71b76cd9f9b4

#grid_results = None

<<<<<<< HEAD
with open('pre_grid_reports.p','rb') as f:
    [grid_results,nparams] = pickle.load(f)
opt_keys = list(grid_results[0].dtc.attrs.keys())
nparams = 2

tests = [electro_tests[0][0][0],electro_tests[0][0][3]]
ga_out = run_ga(model_params,nparams,npoints,tests,provided_keys = opt_keys)
pop = ga_out[0]
new_report = make_report(grid_results, pop, nparams)
reports.update(new_report)

#ga_out = run_ga(model_params,nparams,npoints,tests)

#grid_results = run_grid(nparams,npoints,tests)
with open('pre_ga_reports.p','wb') as f:
    pickle.dump([ga_out,nparams],f)

with open('reports.p','wb') as f:
    pickle.dump(reports,f)
=======
nparams = 2
#tests = electro_tests[0][0][0:2]
'''
grid_results = run_grid(nparams,npoints,tests)
'''

#with open('pre_grid_reports.p','wb') as f:#
#    pickle.dump([grid_results,nparams],f)

#opt_keys = list(copy.copy(grid_results)[0].dtc.attrs.keys())
opt_keys = [str('a'),str('vr')]
ga_out = run_ga(model_params,nparams,npoints,tests,provided_keys = opt_keys)
#pop = ga_out[0]
#new_report = make_report(grid_results, pop, nparams)
reports.update(new_report)
with open('pre_ga_reports.p','wb') as f:
    pickle.dump([ga_out,nparams],f)


with open('pre_ga_reports.p','rb') as f:
    package = pickle.load(f)
>>>>>>> 13fe3fde8c76de2d719acdf82b3a71b76cd9f9b4
