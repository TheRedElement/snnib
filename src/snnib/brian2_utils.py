"""utilities for interactions with `brian2`
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
    """
    for obj in net.objects:
        if isinstance(obj, brian2.SpikeMonitor) and obj.source is group:
            return obj
    return None