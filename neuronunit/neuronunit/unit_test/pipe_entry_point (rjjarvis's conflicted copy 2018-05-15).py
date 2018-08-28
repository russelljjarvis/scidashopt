from neuronunit.optimization import get_neab #import get_neuron_criteria, impute_criteria
import os
import pickle
from neuronunit.optimization.model_parameters import model_params
from bluepyopt.deapext.optimisations import DEAPOptimisation
from neuronunit.tests.fi import RheobaseTestP
from dask import distributed
import pickle

electro_path = 'pipe_tests.p'
fi_basket = {'nlex_id':'NLXCELL:100201'}
# https://scicrunch.org/scicrunch/interlex/view/ilx_0107386
pvis_cortex = {'nlex_id': 'nifext_50'} # Layer V pyramidal cell
#Hippocampal CA1 Pyramidal Neuron
#ca1_pyr = {'nlex_id': 'ILX:0105031' }
#NLXWIKI:sao830368389
# https://scicrunch.org/scicrunch/interlex/view/ilx_0101974
purkinje = { 'nlex_id':'NLXWIKI:sao471801888'} # purkinje
#https://scicrunch.org/scicrunch/interlex/view/ilx_0107933
olf_mitral = { 'nlex_id':'NLXWIKI:nifext_120'}
#https://scicrunch.org/scicrunch/interlex/view/ilx_0107386
ca1_pyr = { 'nlex_id':'SAO:830368389'}
pipe = [ fi_basket, pvis_cortex, ca1_pyr, purkinje, ca1_pyr ]

def pre_process(electro_tests):
    for test,obs in electro_tests:
        test[0] = RheobaseTestP(obs['Rheobase'])
        for k,v in obs.items():
            if v['std'] == 0:
                obs = get_neab.substitute_criteria(electro_tests[1][1],obs)
                print(obs)
    return electro_tests

try:
    assert os.path.isfile(electro_path) == True
    with open(electro_path,'rb') as f:
        electro_tests = pickle.load(f)

except:

    electro_tests = []
    contents[0][0].observation
    for p in pipe:
       p_tests, p_observations = get_neab.get_neuron_criteria(p)
       electro_tests.append((p_tests, p_observations))
    '''
    Add in the parallel rheobase test.
    Substitute out 0'd std deviations in observations with real std deviations.
    '''
    electro_tests = pre_process(electro_tests)

    with open('pipe_tests.p','wb') as f:
       pickle.dump(electro_tests,f)

MU = 6; NGEN = 6; CXPB = 0.9

USE_CACHED_GA = False
provided_keys = list(model_params.keys())

npoints = 2
nparams = 10

electro_tests = pre_process(electro_tests)

cnt = 0
pipe_results = {}
for test, observation in electro_tests:
    dic_key = str(list(pipe[cnt].values())[0])
    DO = DEAPOptimisation(error_criterion = test, selection = 'selIBEA', provided_dict = model_params)
    pop, hof_py, log, history, td_py, gen_vs_hof = DO.run(offspring_size = MU, max_ngen = NGEN, cp_frequency=1,cp_filename=str(dic_key)+'.p')
    #with open(str(dic_key)+'.p','rb') as f:
    #    check_point = pickle.load(f)

    pipe_results[dic_key] = {}
    pipe_results[dic_key]['pop'] = pop# check_point['population']
    pipe_results[dic_key]['hof_py'] = hof_py
    pipe_results[dic_key]['log'] = log # check_point['logbook']
    pipe_results[dic_key]['history'] = history #check_point['history']
    pipe_results[dic_key]['td_py'] = td_py
    pipe_results[dic_key]['gen_vs_hof'] = gen_vs_hof
    cnt += 1
with open('dump_all_cells','wb') as f:
   pickle.dump(pipe_results,f)



    #except:
    #pvis_criterion, pvis_observations = get_neab.get_neuron_criteria(p)

    #inh_criterion, inh_observations = get_neab.get_neuron_criteria(p)
#print(type(inh_observations),inh_observations)

#inh_observations = get_neab.substitute_criteria(pvis_observations,inh_observations)

#inh_criterion, inh_observations = get_neab.get_neuron_criteria(fi_basket,observation = inh_observations)
