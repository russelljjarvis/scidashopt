
import os
import pickle
from dask import distributed
import pickle
import pandas as pd
import timeit

from neuronunit.optimization import get_neab
from neuronunit.optimization.model_parameters import model_params
from bluepyopt.deapext.optimisations import DEAPOptimisation
from neuronunit.optimization.optimization_management import write_opt_to_nml
from neuronunit.optimization import optimization_management
from neuronunit.optimization import optimization_management as om

import numpy as np
import copy


electro_path = 'pipe_tests.p'
purkinje = { 'nlex_id':'sao471801888'}#'NLXWIKI:sao471801888'} # purkinje
fi_basket = {'nlex_id':'100201'}
pvis_cortex = {'nlex_id':'nifext_50'} # Layer V pyramidal cell
olf_mitral = { 'nlex_id':'nifext_120'}
ca1_pyr = { 'nlex_id':'830368389'}
pipe = [ fi_basket, pvis_cortex, olf_mitral, ca1_pyr, purkinje ]
electro_path = 'pipe_tests.p'

try:
    assert os.path.isfile(electro_path) == True
    with open(electro_path,'rb') as f:
        electro_tests = pickle.load(f)
    electro_tests = get_neab.replace_zero_std(electro_tests)
    electro_tests = get_neab.substitute_parallel_for_serial(electro_tests)

except:

    electro_tests = []
    for p in pipe[0:-2]:
       p_tests, p_observations = get_neab.get_neuron_criteria(p)
       electro_tests.append((p_tests, p_observations))

    electro_tests = get_neab.replace_zero_std(electro_tests)
    electro_tests = get_neab.substitute_parallel_for_serial(electro_tests)
    with open('pipe_tests.p','wb') as f:
       pickle.dump(electro_tests,f)

MU = 4; NGEN = 3; CXPB = 0.9
USE_CACHED_GA = False

pipe_results = {}
##
# TODO move to unit testing
##

start_time = timeit.default_timer()
sel = [str('selNSGA2'),str('selIBEA')]

flat_iter = [ (cnt, s, test, observation) for cnt, (test, observation) in enumerate(electro_tests) for s in sel ]
print(flat_iter)

for (cnt,s,test, observation) in flat_iter:
    dic_key = str(list(pipe[cnt].values())[0])
    init_time = timeit.default_timer()
    DO = DEAPOptimisation(error_criterion = test, selection = sel, provided_dict = model_params, elite_size = 3)
    package = DO.run(offspring_size = MU, max_ngen = 6, cp_frequency=1,cp_filename=str(dic_key)+'.p')
    pop, hof, pf, log, history, td_py, gen_vs_hof = package
    finished_time = timeit.default_timer()
    pipe_results[dic_key] = {}
    pipe_results[dic_key]['sel'] = sel

    pipe_results[dic_key]['sel']['duration'] = finished_time - init_time
    pipe_results[dic_key]['sel']['pop'] = copy.copy(pop)
    pipe_results[dic_key]['sel']['hof'] = copy.copy(hof[::-1])
    pipe_results[dic_key]['sel']['pf'] = copy.copy(pf[::-1])
    pipe_results[dic_key]['sel']['log'] = copy.copy(log)
    pipe_results[dic_key]['sel']['history'] = copy.copy(history)
    pipe_results[dic_key]['sel']['td_py'] = copy.copy(td_py)
    pipe_results[dic_key]['sel']['gen_vs_hof'] = copy.copy(gen_vs_hof)
    pipe_results[dic_key]['sel']['sum_ranked_hof'] = [sum(i.dtc.scores.values()) for i in pipe_results[dic_key]['gen_vs_hof'][1:-1]]
    pipe_results[dic_key]['sel']['componentsh'] = [list(i.dtc.scores.values()) for i in pipe_results[dic_key]['gen_vs_hof'][1:-1]]
    pipe_results[dic_key]['sel']['componentsp'] = [list(i.dtc.scores.values()) for i in pipe_results[dic_key]['pf'][1:-1]]

    file_name = str('nlex_id_') + dic_key

    # No, in the notebook, I find a better model to write with other methods.
    #model_to_write = pipe_results[dic_key]['sel']['gen_vs_hof'][-1].dtc.attrs
    optimization_management.write_opt_to_nml(file_name,model_to_write)
    with open('dump_all_cells','wb') as f: pickle.dump(pipe_results,f)

    elapsed = timeit.default_timer() - start_time
    print('entire duration', elapsed)

    times_list = list(pipe_results.values())
    ts = [ t['duration']/60.0 for t in times_list ]
    mean_time = np.mean(ts)
    total_time = np.sum(ts)
