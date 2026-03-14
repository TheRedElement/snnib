"""
TODO

- [ ] for some reason `Test_brian22snnib().test_filecontent()` does not work consistently
    - I suspect that it is a problem with `brian2` scopes interfering with each other
"""

#%%imports
import brian2
from brian2 import (
    start_scope,
    Hz, ms
)
import json
import logging
import os
from pathlib import Path
import pytest

logger = logging.getLogger()
logging.basicConfig(level=logging.ERROR)

from snnib import io
import routines

cur_path = Path(__file__).resolve().parent


#%%global vars
t_sim = 50 * ms
dt = 0.1 * ms
start_scope()
sim1 = routines.brian2_sim(t_sim=t_sim, dt=dt)
start_scope()
sim2 = routines.brian2_sim(t_sim=t_sim, dt=dt, I2=0.6)

#%%tests
class Test_brian22snnib:

    @pytest.fixture(
        params=[
            (sim1[0], f"{cur_path}/temp_snnib1.json", f"{cur_path}/data/test_snnib1.json"),
            # (sim2[0], f"{cur_path}/temp_snnib2.json", f"{cur_path}/data/test_snnib2.json"),
        ]
    )
    def action(self, request):
        #arrange

        #act
        net, fname, fname_true = request.param
        _ = io.brian22snnib(net, t_sim, dt, save=fname, seed=0)

        return (net, fname), (fname_true)
    
    def test_intypes(self, action):
        with pytest.raises(AssertionError):
            (net, fname), (_) = action
            io.brian22snnib("not a net", t_sim, dt, False)
            io.brian22snnib(net, 50, dt, False)
            io.brian22snnib(net, t_sim, 0.1, False)
            io.brian22snnib(net, t_sim, 0.1, "wrong name")
        return
    
    def test_output(self, action):
        (pr, fname), (fname_tr) = action
        assert os.path.exists(fname)

    def test_filecontent(self, action):
        (pr, fname), (fname_tr) = action
        with open(fname, "r") as f:
            data_pr = json.load(f)

        with open(fname_tr, "r") as f:
            data_tr = json.load(f)

        # for k in data_pr.keys():
        #     print("-"*20)
        #     print("\n", k)
        #     # print(data_pr[k])
        #     # print()
        #     # print(data_tr[k])
        #     print(data_pr[k] == data_tr[k])

        assert data_pr == data_tr


