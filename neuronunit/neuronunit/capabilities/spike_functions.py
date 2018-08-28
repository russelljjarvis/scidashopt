"""Auxiliary helper functions for analysis of spiking"""

import numpy as np
import neo
from elephant.spike_train_generation import threshold_detection
from quantities import mV, ms

import sciunit

def get_spike_train(vm, threshold=0.0*mV):
    """
     vm: a neo.core.AnalogSignal corresponding to a membrane potential trace.
     threshold: the value (in mV) above which vm has to cross for there
                to be a spike.  Scalar float.
    Returns:
     a neo.core.SpikeTrain containing the times of spikes.
    """
    spike_train = threshold_detection(vm,threshold=threshold)
    return spike_train

# Membrane potential trace (1D numpy array) to matrix of spike snippets (2D numpy array)
def get_spike_waveforms(vm, threshold=0.0*mV, width=10*ms):
    """
     vm: a neo.core.AnalogSignal corresponding to a membrane potential trace.
     threshold: the value (in mV) above which vm has to cross for there
                to be a spike.  Scalar float.
     width: the length (in ms) of the snippet extracted,
            centered at the spike peak.

    Returns:
     a neo.core.AnalogSignal where each column contains a membrane potential 
     snippets corresponding to one spike.
    """
    spike_train = threshold_detection(vm,threshold=threshold)

    # Fix for 0-length spike train issue in elephant.
    try:
        len(spike_train)
    except TypeError:
        spike_train = neo.core.SpikeTrain([],t_start=spike_train.t_start,
                                             t_stop=spike_train.t_stop,
                                             units=spike_train.units)

    snippets = [vm.time_slice(t-width/2,t+width/2) for t in spike_train]
    result = neo.core.AnalogSignal(np.array(snippets).T.squeeze(),
                                   units=vm.units,
                                   sampling_rate=vm.sampling_rate)
    return result

def spikes2amplitudes(spike_waveforms):
    """
    IN:
     spike_waveforms: Spike waveforms, e.g. from get_spike_waveforms().
        neo.core.AnalogSignal
    OUT:
     1D numpy array of spike amplitudes, i.e. the maxima in each waveform.
    """

    if spike_waveforms is not None:
        ampls = np.max(np.array(spike_waveforms),axis=0)
    else:
        ampls = np.array([])

    return ampls * spike_waveforms.units

def spikes2widths(spike_waveforms):
    """
    IN:
     spike_waveforms: Spike waveforms, e.g. from get_spike_waveforms().
        neo.core.AnalogSignal
    OUT:
     1D numpy array of spike widths, specifically the full width
     at half the maximum amplitude.
    """
    n_spikes = spike_waveforms.shape[1]
    widths = []
    for i in range(n_spikes):
        s = spike_waveforms[:,i].squeeze()
        x_high = int(np.argmax(s))
        high = s[x_high]
        if x_high > 0:
            try: # Use threshold to compute half-max.
                y = np.array(s)
                dvdt = np.diff(y)
                trigger = dvdt.max()/10
                x_loc = int(np.where(dvdt >= trigger)[0][0])
                thresh = (s[x_loc]+s[x_loc+1])/2
                mid = (high+thresh)/2
            except: # Use minimum value to compute half-max.
                sciunit.log(("Could not compute threshold; using pre-spike "
                             "minimum to compute width"))
                low = np.min(s[:x_high])
                mid = (high+low)/2
            n_samples = sum(s>mid) # Number of samples above the half-max.
            widths.append(n_samples)
    widths = np.array(widths,dtype='float')
    if n_spikes:
        # Convert from samples to time.
        widths = widths*spike_waveforms.sampling_period
    return widths

def spikes2thresholds(spike_waveforms):
    """
    IN:
     spike_waveforms: Spike waveforms, e.g. from get_spike_waveforms().
        neo.core.AnalogSignal
    OUT:
     1D numpy array of spike thresholds, specifically the membrane potential
     at which 1/10 the maximum slope is reached.

    If the derivative contains NaNs, probably because vm contains NaNs
    Return an empty list with the appropriate units

    """

    n_spikes = spike_waveforms.shape[1]
    thresholds = []
    for i in range(n_spikes):
        s = spike_waveforms[:,i].squeeze()
        s = np.array(s)
        dvdt = np.diff(s)
        import math
        for j in dvdt:
            if math.isnan(j):
                return thresholds * spike_waveforms.units

        trigger = dvdt.max()/10
        x_loc = np.where(dvdt >= trigger)[0][0]
        thresh = (s[x_loc]+s[x_loc+1])/2
        thresholds.append(thresh)
    return thresholds * spike_waveforms.units
