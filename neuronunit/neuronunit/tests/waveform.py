"""Waveform neuronunit tests, e.g. testing AP waveform properties"""

from .base import np, pq, cap, VmTest, scores, AMPL, DELAY, DURATION


class APWidthTest(VmTest):
    """Tests the full widths of action potentials at their half-maximum."""

    required_capabilities = (cap.ProducesActionPotentials,)

    name = "AP width test"

    description = ("A test of the widths of action potentials "
                   "at half of their maximum height.")

    score_type = scores.ZScore

    units = pq.ms

    ephysprop_name = 'Spike Half-Width'

    def generate_prediction(self, model):
        """Implementation of sciunit.Test.generate_prediction."""
        # Method implementation guaranteed by
        # ProducesActionPotentials capability.
        # if get_spike_count is zero, then widths will be None
        # len of None returns an exception that is not handled
        model.rerun = True

        widths = model.get_AP_widths()
        # Put prediction in a form that compute_score() can use.
        prediction = {'mean':np.mean(widths) if len(widths) else None,
                    'std':np.std(widths) if len(widths) else None,
                    'n':len(widths)}

        return prediction

    def compute_score(self, observation, prediction):
        """Implementation of sciunit.Test.score_prediction."""
        if type(prediction) is type(None):
            score = scores.InsufficientDataScore(None)

        elif prediction['n'] == 0:
            #sciunit.NoneScore:
            score = scores.InsufficientDataScore(None)

        else:
            score = super(APWidthTest,self).compute_score(observation,
                                                          prediction)
        return score


class InjectedCurrentAPWidthTest(APWidthTest):
    """
    Tests the full widths of APs at their half-maximum
    under current injection.
    """
    required_capabilities = (cap.ReceivesSquareCurrent,)

    params = {'injected_square_current':
                {'amplitude':100.0*pq.pA, 'delay':DELAY, 'duration':DURATION}}

    name = "Injected current AP width test"

    description = ("A test of the widths of action potentials "
                   "at half of their maximum height when current "
                   "is injected into cell.")

    def generate_prediction(self, model):
        model.inject_square_current(self.params['injected_square_current'])
        prediction = super(InjectedCurrentAPWidthTest,self).generate_prediction(model)

        return prediction


class APAmplitudeTest(VmTest):
    """Tests the heights (peak amplitude) of action potentials."""

    required_capabilities = (cap.ProducesActionPotentials,)

    name = "AP amplitude test"

    description = ("A test of the amplitude (peak minus threshold) of "
                   "action potentials.")

    score_type = scores.ZScore

    units = pq.mV

    ephysprop_name = 'Spike Amplitude'

    def generate_prediction(self, model):
        """Implementation of sciunit.Test.generate_prediction."""
        # Method implementation guaranteed by
        # ProducesActionPotentials capability.
        model.rerun = True
        heights = model.get_AP_amplitudes() - model.get_AP_thresholds()
        # Put prediction in a form that compute_score() can use.
        prediction = {'mean':np.mean(heights) if len(heights) else None,
                      'std':np.std(heights) if len(heights) else None,
                      'n':len(heights)}
        return prediction

    def compute_score(self, observation, prediction):
        """Implementation of sciunit.Test.score_prediction."""
        if prediction['n'] == 0:
            score = scores.InsufficientDataScore(None)
        else:
            score = super(APAmplitudeTest,self).compute_score(observation,
                                                              prediction)
        return score


class InjectedCurrentAPAmplitudeTest(APAmplitudeTest):
    """
    Tests the heights (peak amplitude) of action potentials
    under current injection.
    """


    required_capabilities = (cap.ReceivesSquareCurrent,)

    params = {'injected_square_current':
                {'amplitude':100.0*pq.pA, 'delay':DELAY, 'duration':DURATION}}

    name = "Injected current AP amplitude test"

    description = ("A test of the heights (peak amplitudes) of "
                   "action potentials when current "
                   "is injected into cell.")

    def generate_prediction(self, model):
        model.inject_square_current(self.params['injected_square_current'])
        prediction = super(InjectedCurrentAPAmplitudeTest,self).\
                generate_prediction(model)
        return prediction


class APThresholdTest(VmTest):
    """Tests the full widths of action potentials at their half-maximum."""

    required_capabilities = (cap.ProducesActionPotentials,)

    name = "AP threshold test"

    description = ("A test of the membrane potential threshold at which "
                   "action potentials are produced.")

    score_type = scores.ZScore

    units = pq.mV

    ephysprop_name = 'Spike Threshold'


    def generate_prediction(self, model):
        """Implementation of sciunit.Test.generate_prediction."""
        # Method implementation guaranteed by
        # ProducesActionPotentials capability.
        model.rerun = True
        threshes = model.get_AP_thresholds()
        # Put prediction in a form that compute_score() can use.
        prediction = {'mean':np.mean(threshes) if len(threshes) else None,
                      'std':np.std(threshes) if len(threshes) else None,
                      'n':len(threshes)}
        return prediction

    def compute_score(self, observation, prediction):
        """Implementation of sciunit.Test.score_prediction."""
        if prediction['n'] == 0:
            score = scores.InsufficientDataScore(None)
        else:
            score = super(APThresholdTest,self).compute_score(observation,
                                                              prediction)
        return score


class InjectedCurrentAPThresholdTest(APThresholdTest):
    """
    Tests the thresholds of action potentials
    under current injection.
    """

    required_capabilities = (cap.ReceivesSquareCurrent,)

    params = {'injected_square_current':
                {'amplitude':100.0*pq.pA, 'delay':DELAY, 'duration':DURATION}}

    name = "Injected current AP threshold test"

    description = ("A test of the membrane potential threshold at which "
                   "action potentials are produced under current injection.")

    def generate_prediction(self, model):
        model.inject_square_current(self.params['injected_square_current'])
        return super(InjectedCurrentAPThresholdTest,self).\
                generate_prediction(model)
