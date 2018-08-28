#import sciunit
class GC():
    def __init__(self):
        self = self

        import allensdk.core.json_utilities as json_utilities
        from allensdk.model.glif.glif_neuron import GlifNeuron
        try:
            from allensdk.api.queries.glif_api import GlifApi
            from allensdk.core.cell_types_cache import CellTypesCache
            import allensdk.core.json_utilities as json_utilities
            import sciunit
        except:
            import os
            os.system('pip install allensdk')
            from allensdk.api.queries.glif_api import GlifApi
            from allensdk.core.cell_types_cache import CellTypesCache
            import allensdk.core.json_utilities as json_utilities
            os.system('pip install git+https://github.com/scidash/sciunit@dev')


        neuronal_model_id = 566302806
        glif_api = GlifApi()
        nc = glif_api.get_neuron_configs([neuronal_model_id])[neuronal_model_id]
        self.nm = GlifNeuron.from_dict(nc)


    def get_membrane_potential(self):
        """Must return a neo.core.AnalogSignal.
        And must destroy the hoc vectors that comprise it.
        """
        dt = float(copy.copy(self.neuron.dt))
        import pdb;
        pdb.set_trace()
        #return data.filter(name="v")[0]

    def _local_run(self,amp):
        '''
        pyNN lazy array demands a minimum population size of 3. Why is that.
        '''
        import numpy as np
        results = {}
        # important! set the neuron's dt value for your stimulus in seconds
        stim = [ 0.0 ] * 100 + [ amp ] * 100 + [ 0.0 ] * 100

        self.nm.run(stim)
        import pdb; pdb.set_trace()
        return results


    def set_attrs(self):#, **attrs):
        nc = glif_api.get_neuron_configs([neuronal_model_id])[neuronal_model_id]
        neuron_config = glif_api.get_neuron_configs([neuronal_model_id])
        #nc = glif_api.get_neuron_configs([neuronal_model_id])[neuronal_model_id]
        #neuron_config = glif_api.get_neuron_configs([neuronal_model_id])

        neuron_config = neuron_config['566302806']
        self.nm = GlifNeuron.from_dict(neuron_config)
        return self.nm

    def inject_square_current(self, current):
        ctc.get_ephys_data(nm['specimen_id'], file_name='stimulus.nwb')
        ctc.get_ephys_sweeps(nm['specimen_id'], file_name='ephys_sweeps.json')
        self.ctc = ctc

        import copy
        attrs = copy.copy(self.model.attrs)
        self.init_backend()
        self.set_attrs(**attrs)
        c = copy.copy(current)
        if 'injected_square_current' in c.keys():
            c = current['injected_square_current']

        c['delay'] = re.sub('\ ms$', '', str(c['delay'])) # take delay
        c['duration'] = re.sub('\ ms$', '', str(c['duration']))
        c['amplitude'] = re.sub('\ pA$', '', str(c['amplitude']))
        stop = float(c['delay'])+float(c['duration'])
        start = float(c['delay'])
        amplitude = float(c['amplitude'])/1000.0
        #stimulus = [ 0.0 ] * 100 + [ amplitude ] * 100 + [ 0.0 ] * 100
        stim = [ 0.0 ] * 100 + [ amplitude ] * 100 + [ 0.0 ] * 100
        self.nm.run(stim)
