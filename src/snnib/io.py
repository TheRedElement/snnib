"""
"""

#%%imports
import brian2
import brian2.numpy_ as np
import json
import logging

from . import brian2_utils as snnib_b2u

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.WARNING)

#%%definitions
def brian22snnib(
    net:brian2.Network,
    t_sim:brian2.Quantity, dt:brian2.Quantity,
    save:str=False,
    ):
    """saves `net` to `snnib` compliant json file
    """
    ngs = [obj for obj in net.objects if isinstance(obj, brian2.NeuronGroup)]
    sgs = [obj for obj in net.objects if isinstance(obj, brian2.Synapses)]

    meta = dict(    #simulation metadata
        t_sim=float(t_sim), t_sim_unit=str(t_sim.dimensions),
        dt=float(dt), dt_unit=str(dt.dimensions),
        steps=int(t_sim/dt)                                     #number of steps (assuming constant `dt`)
    )

    #get synapses
    synapses_snnib = dict(pre=[], post=[], w=[], w_unit=[])
    for sg in sgs:
        synapses_snnib["pre"]       += sg.i[:].tolist()
        synapses_snnib["post"]      += sg.j[:].tolist()
        synapses_snnib["w"]         += np.asarray(sg.w[:]).tolist() #remove unit
        synapses_snnib["w_unit"]    += [str(sg.w[0].dimensions)] * sg.i[:].shape[0]

    #reformat
    synapses_snnib = list(zip(*synapses_snnib.values()))   #transpose

    #get neurons
    neurons_snnib = dict(id=[], x=[], y=[], z=[], spiketrain=[], spiketrain_unit=[])
    for ng in ngs:
        neurons_snnib["id"] += ng.i[:].tolist()
        
        #generate random coordinates
        neurons_snnib["x"] += ((np.random.rand(ng.i.shape[0])-0.5)*2).tolist()
        neurons_snnib["y"] += ((np.random.rand(ng.i.shape[0])-0.5)*2).tolist()
        neurons_snnib["z"] += ((np.random.rand(ng.i.shape[0])-0.5)*2).tolist()

        #get spiketrains
        spiketrains = list(snnib_b2u.get_spike_monitor(net, ng).spike_trains().values())
        spiketrain_unit = spiketrains[0].dimensions
        spiketrains = [(st / dt).astype(int).tolist() for st in spiketrains]    #convert spiketrains to simulations steps
        neurons_snnib["spiketrain"]      += spiketrains
        neurons_snnib["spiketrain_unit"] +=  [str(spiketrain_unit)] * ng.i.shape[0]

    neurons_snnib = list(zip(*list(neurons_snnib.values())[1:]))    #transpose #remove ID because encoded in index
    # print(meta)
    # print(synapses_snnib)
    # print(neurons_snnib)

    if isinstance(save, str):
        with open(save, "w") as f:
            json.dump(dict(
                meta=meta,
                neurons=neurons_snnib,
                synapses=synapses_snnib
            ), f)
    return