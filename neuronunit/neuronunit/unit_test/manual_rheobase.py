from neuronunit.models.reduced import ReducedModel
from neuronunit.optimization.model_parameters import model_params, path_params
from neuronunit.optimization import model_parameters as modelp
mp = modelp.model_params
import pdb
from neuronunit.optimization.data_transport_container import DataTC
dtc = DataTC()
from neuronunit.tests import np, pq, cap, VmTest, scores, AMPL, DELAY, DURATION


opt_keys = ['a','b','vr']
nparams = len(opt_keys)
import numpy as np
attrs = {'a':np.median(mp['a']), 'b':np.median(mp['b']), 'vr':np.median(mp['vr'])}
dtc.attrs = attrs
model = ReducedModel(path_params['model_path'],name = str('vanilla'),backend =('NEURON',{'DTC':dtc}))

params = {'injected_square_current':
            {'amplitude':10.0*pq.pA, 'delay':DELAY, 'duration':DURATION}}

model.inject_square_current(params)
n_spikes = model.get_spike_count()
print(n_spikes)
