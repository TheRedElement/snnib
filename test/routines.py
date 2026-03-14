"""functions and routines used in testing
"""

#%%imports
import brian2
from brian2 import (
    NeuronGroup,
    Synapses,
    SpikeMonitor,
    ms,
)

#%%definitions

def brian2_sim(
    t_sim:brian2.Quantity=50*ms, dt:brian2.Quantity=0.2*ms,
    n_neurons1:int=3, n_neurons2:int=3,
    #neuron params
    I1:float=0.2, I2:float=0.0,
    tau:brian2.Quantity=1*ms,
    #synapse params
    w0:float=0.5,
    ):
    """very basic brian2 simulation for testing

    Parameters
        - `t_sim`
            - `brian2.Quantity`
            - simulation time
        - `dt`
            - `brian2.Quantity`
            - simulation step
        - `n_neurons1`
            - `int`
            - number of neurons of the neuron group 1
        - `n_neurons2`
            - `int`
            - number of neurons of the neuron group 2
        - `I1`
            - `float`
            - input to neuron group 1
        - `I2`
            - `float`
            - input to neuron group 2
        - `tau`
            - `brian2.Quantity`
            - time constant of the neurons
        - `w0`
            - `float`
            - initial synapse weight

    Raises

    Returns
        - `net()`
            - `brian2.Network`
            - created network
        - `G1()`
            - `brian2.NeuronGroup`
            - created neuron group
        - `G2()`
            - `brian2.NeuronGourp`
            - created neuron group
        - `S()`
            - `brian2.Synapses`
            - created synapses
        - `M1()`
            - `brian2.SpikeMonitor`
            - created spike monitor
        - `M2()`
            - `brian2.SpikeMonitor`
            - created spike monitor

    Dependencies
        - `brian2`
    """

    
    # simulation timestep
    brian2.defaultclock.dt = dt

    #neuron model (simple integrator)
    eqs = '''
    dv/dt = I/(tau) : 1
    I : 1
    '''

    G1 = NeuronGroup(
        n_neurons1,
        eqs,
        threshold='v > 1',
        reset='v = 0',
        method='euler'
    )

    G2 = NeuronGroup(
        n_neurons2,
        eqs,
        threshold='v > 1',
        reset='v = 0',
        method='euler'
    )

    #neuron input
    G1.I = I1
    G2.I = I2

    #synapses
    s_eqs = '''
    w : 1
    '''
    S = Synapses(G1, G2, s_eqs, on_pre='v_post += w')
    S.connect(j='i')                                #one-to-one connections
    S.w = w0                                        #init weights

    #spike monitors
    M1 = SpikeMonitor(G1)
    M2 = SpikeMonitor(G2)

    parts = [
        G1, G2,
        S,
        M1, M2,
    ]
    net = brian2.Network(parts)

    #simulate
    net.run(t_sim)

    #some detached elements
    G_detached = NeuronGroup(1, eqs)    #to test output when neuron group does not exist in `net`

    return (net,
        G1, G2,
        S,
        M1, M2,
        #elements not included in `net` (for stress-testing)
        G_detached,
    )
