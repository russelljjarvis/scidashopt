"""Tests for ephys.efeatures"""

import os
from os.path import join as joinp
import nose.tools as nt
from nose.plugins.attrib import attr

from bluepyopt.ephys import efeatures
from bluepyopt.ephys.responses import TimeVoltageResponse
from bluepyopt.ephys.serializer import instantiator


@attr('unit')
def test_EFeature():
    """ephys.efeatures: Testing EFeature creation"""
    efeature = efeatures.EFeature('name')
    nt.eq_(efeature.name, 'name')


@attr('unit')
def test_eFELFeature():
    """ephys.efeatures: Testing eFELFeature creation"""
    recording_names = {'': 'square_pulse_step1.soma.v'}
    efeature = efeatures.eFELFeature(name='test_eFELFeature',
                                     efel_feature_name='voltage_base',
                                     recording_names=recording_names,
                                     stim_start=700,
                                     stim_end=2700,
                                     exp_mean=1,
                                     exp_std=1)

    response = TimeVoltageResponse('mock_response')
    testdata_dir = joinp(os.path.dirname(os.path.abspath(__file__)), 'testdata')
    response.read_csv(joinp(testdata_dir, 'TimeVoltageResponse.csv'))
    responses = {'square_pulse_step1.soma.v': response, }

    ret = efeature.calculate_feature(responses, raise_warnings=True)
    nt.assert_almost_equal(ret, -72.069487699766668)

    score = efeature.calculate_score(responses)
    nt.assert_almost_equal(score, 73.06948769976667)

    nt.eq_(efeature.name, 'test_eFELFeature')
    nt.ok_('voltage_base' in str(efeature))


@attr('unit')
def test_eFELFeature_double_settings():
    """ephys.efeatures: Testing eFELFeature double_settings"""
    recording_names = {'': 'square_pulse_step1.soma.v'}
    efeature = efeatures.eFELFeature(name='test_eFELFeature',
                                     efel_feature_name='voltage_base',
                                     recording_names=recording_names,
                                     stim_start=700,
                                     stim_end=2700,
                                     exp_mean=1,
                                     exp_std=1)
    efeature_ds = efeatures.eFELFeature(
        name='test_eFELFeature_other_perc',
        efel_feature_name='voltage_base',
        recording_names=recording_names,
        stim_start=700,
        stim_end=2700,
        exp_mean=1,
        exp_std=1,
        double_settings={
            'voltage_base_start_perc': 0.01})

    response = TimeVoltageResponse('mock_response')
    testdata_dir = joinp(os.path.dirname(os.path.abspath(__file__)), 'testdata')
    response.read_csv(joinp(testdata_dir, 'TimeVoltageResponse.csv'))
    responses = {'square_pulse_step1.soma.v': response, }

    vb_other_perc = efeature_ds.calculate_feature(
        responses,
        raise_warnings=True)
    vb = efeature.calculate_feature(responses, raise_warnings=True)

    nt.assert_true(vb_other_perc != vb)


def test_eFELFeature_serialize():
    """ephys.efeatures: Testing eFELFeature serialization"""
    recording_names = {'': 'square_pulse_step1.soma.v'}
    efeature = efeatures.eFELFeature(name='test_eFELFeature',
                                     efel_feature_name='voltage_base',
                                     recording_names=recording_names,
                                     stim_start=700,
                                     stim_end=2700,
                                     exp_mean=1,
                                     exp_std=1)
    serialized = efeature.to_dict()
    deserialized = instantiator(serialized)
    nt.ok_(isinstance(deserialized, efeatures.eFELFeature))
    nt.eq_(deserialized.stim_start, 700)
    nt.eq_(deserialized.recording_names, recording_names)
