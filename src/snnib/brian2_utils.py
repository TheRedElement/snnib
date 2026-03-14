"""utilities for interactions with `brian2`

- functions and classes to make interaction with `brian2` objects more straightforward

Exceptions

Classes

Functions
    - `get_spike_monitor()` -- obtains a `SpikeMonitor` associated with some `NeuronGroup`
    - `get_spiketrain()` -- obtains plottable spiketrain from some `SpikeMonitor`

Other Objects
"""

#%%imports
import brian2
import logging

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.WARNING)

#%%definitions
def get_spike_monitor(
    net:brian2.Network, group:brian2.NeuronGroup
    ) -> brian2.SpikeMonitor:
    """returns the `SpikeMonitor` associated to `group` if it exists

    - returns only the first found `SpikeMonitor`
    - returns `None` if no `SpikeMonitor` was found

    Parameters
        - `net`
            - `brian2.Network`
            - network to hosting `group`
        - `group`
            - `brian2.NeuronGroup`
            - neuron group to get the `SpikeMonitor` of
    
    Raises

    Returns
        - `obj`
            - `SpikeMonitor`
            - extracted `SpikeMonitor`
            - `None` if no `SpikeMonitor` was found

    Dependencies
        - `brian2`
        - `logging`
        
    """
    #checks
    assert isinstance(net, brian2.Network)
    assert isinstance(group, brian2.groups.Group)

    for obj in net.objects:
        if isinstance(obj, brian2.SpikeMonitor) and obj.source is group:
            return obj
    logger.info("no `SpikeMonitor` found")
    return None

def get_spiketrains(
    spike_mon:brian2.SpikeMonitor,
    t_max:brian2.Quantity,
    n2plot:int
    ):
    """returns spiketrains of the first `n2plot` neurons contained in `spike_mon`

    Parameters
        - `spike_mon`
            - `brian2.SpikeMonitor`
            - spike monitor containing the spiketrains
        - `t_max`
            - `brian2.Quantity`
            - maximum time to extract spiketrains for
        - `n2plot`
            - `int`
            - number of neurons to extract spiketrains for

    Raises

    Returns
        - `times`
            - `np.array[brian2.Quantity]`
            - extracted spike times
        - `ids`
            - `np.array`
            - ids of the neurons the spiketrains of which have been extracted
    
    Dependencies
    """
    times, ids = spike_mon.t[:], spike_mon.i[:]
    mask = (times <= t_max) & (ids < n2plot)
    
    return times[mask], ids[mask]