#%%imports
import brian2
from brian2 import (
    PoissonGroup,
    SpikeMonitor,
    Hz, ms
)
import logging
import pytest
import numpy as np

logger = logging.getLogger()
logging.basicConfig(level=logging.ERROR)

from snnib import brian2_utils
import routines


#%%global vars
t_sim = 50 * ms
(
    #actual outputs
    net, G1, G2, S, M1, M2,
    #outputs not contained in `net` (to stress-test)
    G_detached,
) = routines.brian2_sim(t_sim=t_sim)

#%%tests
class Test_get_spike_monitor:

    @pytest.fixture(
        params=[
            (net, G1, M1, M1),
            (net, G2, M2, M2),
            (net, G_detached, M1, None),
        ]
    )
    def action(self, request):
        #arrange

        #act
        net, G, M, M_true = request.param
        M_pred = brian2_utils.get_spike_monitor(net, G)

        return M_pred, M_true
    
    def test_intypes(self, action):
        with pytest.raises(AssertionError):
            brian2_utils.get_spike_monitor("not a net", G1)
            brian2_utils.get_spike_monitor(net, "not a ng")

        return
    
    def test_outtypes(self, action):
        pr, tr = action
        assert isinstance(pr, brian2.SpikeMonitor) or pr is None

    
    def test_output(self, action):
        pr, tr = action
        assert pr == tr


class Test_get_spiketrain:

    @pytest.fixture(
        params=[
            (M1, t_sim, 5,
                np.array([ 4.8,  4.8,  4.8,  9.8,  9.8,  9.8, 14.8, 14.8, 14.8, 19.8, 19.8, 19.8, 24.8, 24.8, 24.8, 29.8, 29.8, 29.8, 34.8, 34.8, 34.8, 39.8, 39.8, 39.8, 44.8, 44.8, 44.8, 49.8, 49.8, 49.8]) * ms,
                np.array([0, 1, 2, 0, 1, 2, 0, 1, 2, 0, 1, 2, 0, 1, 2, 0, 1, 2, 0, 1, 2, 0,1, 2, 0, 1, 2, 0, 1, 2]),
            ),
            (M2, t_sim, 5,
                np.array([15., 15., 15., 30., 30., 30., 45., 45., 45.]) * ms,
                np.array([0, 1, 2, 0, 1, 2, 0, 1, 2]),
            ),
            (M1, 25 * ms, 2,
                np.array([ 4.8,  4.8,  9.8,  9.8, 14.8, 14.8, 19.8, 19.8, 24.8, 24.8]) * ms,
                np.array([0, 1, 0, 1, 0, 1, 0, 1, 0, 1]),
            ),
        ]
    )
    def action(self, request):
        #arrange

        #act
        M, t_max, n2plot, t_true, i_true = request.param
        t_pred, i_pred = brian2_utils.get_spiketrains(M, t_max, n2plot)
        return (t_pred, i_pred), (t_true, i_true)
    
    def test_output(self, action):
        (t_pr, i_pr), (t_tr, i_tr) = action

        assert t_pr / ms == pytest.approx(t_tr / ms)    #remove units to avoid precision errors
        assert np.all(i_pr == i_tr)