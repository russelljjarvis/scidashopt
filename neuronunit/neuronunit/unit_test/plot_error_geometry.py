
# coding: utf-8

# In[1]:
import matplotlib
matplotlib.use('agg')


from neuronunit.models.reduced import ReducedModel
from neuronunit.optimization.model_parameters import model_params, path_params
from neuronunit.optimization import model_parameters as modelp
mp = modelp.model_params
import pdb
from neuronunit.optimization.data_transport_container import DataTC
dtc = DataTC()
from neuronunit.tests import np, pq, cap, VmTest, scores, AMPL, DELAY, DURATION
from neuronunit.models.backends import pyNN
try:
    import lazyarray
    import mpi4py
except:
    get_ipython().system('pip install lazyarray')
    get_ipython().system('pip install mpi4py')
    import lazyarray



import pickle,os
from neuronunit.optimization import get_neab
electro_path = str(os.getcwd())+'/pipe_tests.p'
print(os.getcwd())
assert os.path.isfile(electro_path) == True
with open(electro_path,'rb') as f:
    electro_tests = pickle.load(f)

electro_tests = get_neab.replace_zero_std(electro_tests)
electro_tests = get_neab.substitute_parallel_for_serial(electro_tests)
tests, observation = electro_tests[0]

from neuronunit.optimization import model_parameters as modelp



# In[2]:



model = ReducedModel(path_params['model_path'],name = str('regular_spiking'),backend =('NEURON',{'DTC':dtc}))

params = {'injected_square_current':
            {'amplitude': 11.0*pq.pA, 'delay':DELAY, 'duration':DURATION}}

model.inject_square_current(params)
n_spikes = model.get_spike_count()
vmrs2 = model.get_membrane_potential()
print(n_spikes)



# # regular spiking cell (RS)
#

# In[3]:


attrs = {}
attrs['c'] = -50
attrs['vr'] = -60
attrs['vt'] = -40
attrs['vpeak'] = 35


attrs['C'] = 100E-4
attrs['k'] = 0.7E-4
attrs['a'] = 0.03E-4
attrs['b'] = -2E-4
attrs['d'] = 100E-4



DELAY = 100
DURATION = 800
dtc.attrs = attrs

neuron = None

modelrs = ReducedModel(path_params['model_path'],name = str('regular_spiking'),backend =('NEURON',{'DTC':dtc}))

params = {'injected_square_current':
            {'amplitude': 21.0*pq.pA, 'delay':DELAY, 'duration':DURATION}}

modelrs.inject_square_current(params)
n_spikes = modelrs.get_spike_count()
print(n_spikes)
vmrs = modelrs.get_membrane_potential()


# In[ ]:





# In[4]:


#              C    k     vr  vt vpeak   a      b   c    d  celltype
# ('RS',     (100, 0.7,  -60, -40, 35, 0.03,   -2, -50,  100,  1)),

attrs = {}
attrs['c'] = -50
attrs['vr'] = -60
attrs['vt'] = -40
attrs['vpeak'] = 35

#hof[0].dtc.attrs
#Out[6]: {'a': 0.0001100000055, 'b': 30.0, 'vr': -40.0}
attrs['C'] = -100*10**-4
attrs['k'] = 0.7E-4
attrs['a'] = 0.0001100000055
attrs['b'] = -30.0*10**-4
attrs['d'] = 100E-4

dtc.attrs = attrs



DELAY = 100
DURATION = 800
neuron = None

modelp = ReducedModel(path_params['model_path'],name = str('regular_spiking'),backend =('NEURON',{'DTC':dtc}))
observations = {}
predictions = {}

scores = {}
import dask.bag as db
for t in tests:
    LEMS_MODEL_PATH = path_params['model_path']
    model = ReducedModel(LEMS_MODEL_PATH,name=str('vanilla'),backend='NEURON')
    model.set_attrs(dtc.attrs)
    score = t.judge(model)
    scores[str(t)] = score
    observations[str(t)] = score.observation
    predictions[str(t)] = score.prediction


def dic_reductions(observations,predictions):

    simple_pa = { k:v['value'] for k,v in predictions.items() if 'value' in v.keys() }
    simple_pa.update({ k:v['mean'] for k,v in predictions.items() if 'mean' in v.keys() })
    simple_p = { k:v for k,v in simple_pa.items() if 'AP' in k or 'RestingPotentialTest' in k}



    simple_obsa = { k:v['value'] for k,v in observations.items() if 'value' in v.keys() }
    simple_obsa.update({ k:v['mean'] for k,v in observations.items() if 'mean' in v.keys() })
    simple_obs = { k:v for k,v in simple_obsa.items() if 'AP' in k or 'RestingPotentialTest' in k }


    deltas = {k:simple_p[k]-v for k,v in simple_obs.items() }
    return simple_p, simple_obs, deltas
import seaborn as sns
sns.set()
import matplotlib.pyplot as plt

import matplotlib.pyplot as plt
def plot(vm,plt):
    times = vm.times
    plt.plot(times,vm)
    plt.xlabel('ms')
    plt.ylabel('mV')
    return plt

#def plot_error_geom(vm,plt,obs,pred,deltas,model):
def plot_error_geom(vm,plt,obs,pred,deltas,model,rh):


    #vm = model.get_membrane_potential()
    times = vm.times
    st = model.get_spike_train()
    if len(st) > 1:
        st = st[0]

    for k,v in pred.items():
        if 'InjectedCurrentAPWidthTest' not in k:
            p = [float(pred[k]) for i in times]
            o = [float(obs[k]) for i in times]
            #plt.fill(x, Y, facecolor='blue', alpha=0.5)
            plt.fill_between(o, p, times, alpha=0.5)
            plt.plot(times,p,label = str('prediction ')+str(k))
            plt.plot(times,o,label = str('observation ')+str(k))
        else:
            intervalp = pred[k]
            newti = []
            for i in times:
                if i < st:
                    newti.append(pred['InjectedCurrentAPThresholdTest'])

                if i >= st and i <= intervalp*10000.0 + st:
                    newti.append(pred['InjectedCurrentAPAmplitudeTest'])

                if i > intervalp*10000.0 + st:
                    newti.append(pred['InjectedCurrentAPThresholdTest'])

                #print(len(times),len(newti))
            plt.plot(times,newti,label='spike width')



        plt.plot(times,vm)

    plt.xlabel('ms')
    plt.ylabel('mV')
    plt.legend(loc=2, fontsize = 'x-small')
    #plt.legend()
    #plt
    return plt
vm = model.get_membrane_potential()

simple_p, simple_obs, deltas = dic_reductions(observations,predictions)
rh = simple_p.keys()
print(rh)
import pdb; pdb.set_trace()
#plot_lines(vm, plt, simple_obs, simple_p, deltas, model,rh)
plt = plot_error_geom(vm,plt,simple_obs,simple_p,deltas,model,rh)
plt.savefig('blah.png')
sort_scores = {k:1.0-v.sort_key for k,v in scores.items() }


import pandas as pd
import seaborn as sns
dfs = pd.DataFrame.from_dict(pd.Series(sort_scores), orient='columns')

dfg = dfs.reset_index(drop=True)

# Set colormap equal to seaborns light green color palette
cm = sns.light_palette("green", as_cmap=True)
display(dfg.style.background_gradient(cmap=cm))


# In[ ]:


plt = plot(vmrs2,plt)
plt.show()


# Chattering
#

# In[ ]:


plt.clf()
plt = plot(vmrs,plt)
plt.show()


# In[ ]:


#C = 50     vr = -60     vt = -40     k = 1.5
#a = 0.03     b = 1     c = -40     d = 150     vPeak = 35

attrs['vr'] = -60
attrs['vt'] = -40
attrs['c'] = -40
attrs['vpeak'] = 35




attrs['C'] = 50E-4
attrs['k'] = 1.5E-4
attrs['a'] = 0.03E-4
attrs['b'] = 1E-4
attrs['d'] = 150E-4




modelch = ReducedModel(path_params['model_path'],name = str('chattering'),backend =('NEURON',{'DTC':dtc}))

params = {'injected_square_current':
            {'amplitude': 300*pq.pA, 'delay':DELAY, 'duration':DURATION}}

modelch.inject_square_current(params)
n_spikes = modelch.get_spike_count()
vmch = modelch.get_membrane_potential()
print(n_spikes)

plt = plot(vmch,plt)
plt.show()



# In[ ]:


'''

x                       % time step  [ms]

http://www.physics.usyd.edu.au/teach_res/mp/ns/doc/nsIzhikevich3.htm
https://www.izhikevich.org/publications/izhikevich.m-
a=pars(1,1);
b=pars(1,2);
c=pars(1,3);
d=pars(1,4);
I=pars(1,5);



figNumber = figure(1);
clf;
set(figNumber,'NumberTitle','off','doublebuffer','on',...
        'Name','Simple Model by Izhikevich (2003)',...
        'Units','normalized','toolbar','figure',...
        'Position',[0.05 0.1 0.9 0.8]);
h1=subplot(4,2,1);
set(h1,'Position',[0.05 0.75 0.27 0.2])
vtrace=line('color','k','LineStyle','-','erase','background','xdata',[],'ydata',[],'zdata',[]);
axis([0 100 -100 30])
title('membrane potential, v')
xlabel('time (ms)');
'''
