#%%imports
import brian2
from brian2 import (
    PoissonGroup,
    SpikeMonitor,
    Hz,
)
import logging
import pytest
import numpy as np

logger = logging.getLogger()
logging.basicConfig(level=logging.ERROR)

from snnib import brian2_utils
import routines


#%%global vars
(
    #actual outputs
    net, G1, G2, S, M1, M2,
    #outputs not contained in `net` (to stress-test)
    G_detached,
) = routines.brian2_sim()

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