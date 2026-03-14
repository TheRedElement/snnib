"""module for input-output operations

- utilities to convert models generated with various SNN simulators to `SNNIB` format

Exceptions

Classes

Functions
    - `brian22snnib()` -- converts `brian2` network to `SNNIB`

Other Objects
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
    seed:int=None,
    ):
    """saves `net` to `snnib` compatible json file

    - function to convert `brian2` network to a file that can be imported using `SNNIB`
        - uses `net` to obtain network elements (synapses, neurons, spiketrains)
        - generates random 3d coordinates $\vec x \in [-1,1]$ for each neuron
        - removes units (stores them separately)
        - extracts some simulation metadata

    Parameters
        - `net`
            - `brian2.Network`
            - the network object to convert to `SNNIB` format
        - `t_sim`
            - `brian2.Quantity`
            - simulation time of the `brian2` simulation
        - `dt`
            - `brian2.Quantity`
            - time-step of the `brian2` simulation
        - `save`
            - `str`, optional
            - file to save the result to
            - the default is `False`
                - result not saved

    Raises

    Returns
        - `snnib_obj`
            - `dict`
            - json
            - generated object that is compatible with SNNIB

    
    Dependencies
        - `brian2`
        - `json`
        - `logging`
    
    
    """
    
    #checks
    assert isinstance(net, brian2.Network)
    assert isinstance(t_sim, brian2.Quantity)
    assert isinstance(dt, brian2.Quantity)
    assert isinstance(save, (str,bool))
    if isinstance(save, str):
        assert save.endswith(".json"), "`save` has to be a json file"
    
    #setup rng
    Rng = np.random.default_rng(seed)

    #get network objects
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
        if isinstance(sg.w[0], brian2.Quantity):
            synapses_snnib["w_unit"]    += [str(sg.w[0].dimensions)] * sg.i[:].shape[0]
        else:
            synapses_snnib["w_unit"]    += [""] * sg.i[:].shape[0]

    #reformat
    synapses_snnib = list(zip(*synapses_snnib.values()))   #transpose

    #get neurons
    neurons_snnib = dict(id=[], x=[], y=[], z=[], spiketrain=[], spiketrain_unit=[])
    for ng in ngs:
        neurons_snnib["id"] += ng.i[:].tolist()
        
        #generate random coordinates
        neurons_snnib["x"] += ((Rng.random(ng.i.shape[0])-0.5)*2).tolist()
        neurons_snnib["y"] += ((Rng.random(ng.i.shape[0])-0.5)*2).tolist()
        neurons_snnib["z"] += ((Rng.random(ng.i.shape[0])-0.5)*2).tolist()

        #get spiketrains
        spiketrains = list(snnib_b2u.get_spike_monitor(net, ng).spike_trains().values())
        spiketrain_unit = spiketrains[0].dimensions
        spiketrains = [(st / dt).astype(int).tolist() for st in spiketrains]    #convert spiketrains to simulations steps
        neurons_snnib["spiketrain"]      += spiketrains
        neurons_snnib["spiketrain_unit"] +=  [str(spiketrain_unit)] * ng.i.shape[0]

    neurons_snnib = list(zip(*list(neurons_snnib.values())[1:]))    #transpose #remove ID because encoded in index
    logger.debug(meta)
    logger.debug(synapses_snnib)
    logger.debug(neurons_snnib)

    snnib_obj = dict(
        meta=meta,
        neurons=neurons_snnib,
        synapses=synapses_snnib
    )

    if isinstance(save, str):
        with open(save, "w") as f:
            json.dump(snnib_obj, f)
    
    return snnib_obj
