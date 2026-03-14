"""utilities for interactions with `brian2`

- functions and classes to make interaction with `brian2` objects more straightforward

Exceptions

Classes

Functions
    - `get_spike_monitor()` -- obtains a `SpikeMonitor` associated with some `NeuronGroup`

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