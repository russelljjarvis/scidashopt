"""NeuronUnit abstract Capabilities"""
# The goal is to enumerate all possible capabilities of a model 
# that would be tested using NeuronUnit.
# These capabilities exchange 'neo' objects.

import inspect

import numpy as np

import sciunit
from .spike_functions import spikes2amplitudes,spikes2widths,spikes2thresholds


class ProducesMembranePotential(sciunit.Capability):
    """Indicates that the model produces a somatic membrane potential."""

    def get_membrane_potential(self, **kwargs):
        """Must return a neo.core.AnalogSignal."""
        raise NotImplementedError()

    def get_mean_vm(self, **kwargs):
        vm = self.get_membrane_potential(**kwargs)
        return np.mean(vm.base)

    def get_median_vm(self, **kwargs):
        vm = self.get_membrane_potential(**kwargs)
        return np.median(vm.base)

    def get_std_vm(self, **kwargs):
        vm = self.get_membrane_potential(**kwargs)
        return np.std(vm.base)

    def get_iqr_vm(self, **kwargs):
        vm = self.get_membrane_potential(**kwargs)
        return (np.percentile(vm,75) - np.percentile(vm,25))*vm.units

    def get_initial_vm(self,**kwargs):
        """Returns a quantity corresponding to the starting membrane potential.
        This will in some cases be the resting potential."""
        vm = self.get_membrane_potential(**kwargs)
        # A neo.core.AnalogSignal object
        return vm[0]


class ProducesSpikes(sciunit.Capability):
    """Indicates that the model produces spikes.
    No duration is required for these spikes.
    """

    def get_spike_train(self):
        """Gets computed spike times from the model.

        Arguments: None.
        Returns: a neo.core.SpikeTrain object.
        """

        raise NotImplementedError()

    def get_spike_count(self):
        spike_train = self.get_spike_train()
        return len(spike_train)


class ProducesActionPotentials(ProducesSpikes, 
                               ProducesMembranePotential):
    """Indicates the model produces action potential waveforms.
    Waveforms must have a temporal extent.
    """

    def get_APs(self):
        """Gets action potential waveform chunks from the model.

        Returns
        -------
        Must return a neo.core.AnalogSignal.
        Each column of the AnalogSignal should be a spike waveform.
        """

        raise NotImplementedError()

    def get_AP_widths(self):
        action_potentials = self.get_APs()
        widths = spikes2widths(action_potentials)
        return widths

    def get_AP_amplitudes(self):
        action_potentials = self.get_APs()
        amplitudes = spikes2amplitudes(action_potentials)
        return amplitudes

    def get_AP_thresholds(self):
        action_potentials = self.get_APs()
        thresholds = spikes2thresholds(action_potentials)
        return thresholds


class ReceivesSquareCurrent(sciunit.Capability):
    """Indicates that somatic current can be injected into the model as
    a square pulse.
    """

    def inject_square_current(self, current):
        """Injects somatic current into the model.

        Parameters
        ----------
        current : a dictionary like:
                        {'amplitude':-10.0*pq.pA,
                         'delay':100*pq.ms,
                         'duration':500*pq.ms}}
                  where 'pq' is the quantities package
        This describes the current to be injected.
        """
        raise NotImplementedError()


class ReceivesCurrent(ReceivesSquareCurrent):
    """Indicates that somatic current can be injected into the model as
    either an arbitrary waveform or as a square pulse.
    """

    def inject_current(self, current):
        """Injects somatic current into the model.

        Parameters
        ----------
        current : neo.core.AnalogSignal
        This is a time series of the current to be injected.
        """

        raise NotImplementedError()


class Runnable(sciunit.Capability):
    """Capability for models that can be run."""
    
    def run(self, **run_params):
        return NotImplementedError("%s not implemented" % inspect.stack()[0][3])
