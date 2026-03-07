"""
"""

#%%imports
import argparse
import brian2
from brian2 import NeuronGroup, PoissonInput, SpikeGeneratorGroup, SpikeMonitor, StateMonitor, Synapses
from brian2 import mV, pA, pF, ms, second, Hz, Gohm
import brian2.numpy_ as np
import logging
from typing import Any, Literal

logging.basicConfig(level=logging.WARN, force=True)
local_logger = logging.getLogger(__name__)
local_logger.setLevel(logging.DEBUG)

#%%from tasksheet
def poisson_generator(rate, t_lim, unit_ms=False):
    """
    Draw events from a Poisson point process.

    Note: the implementation assumes at t=t_lim[0], although this spike is not
    included in the spike list.

    :param rate: the rate of the discharge in Hz
    :param t_lim: tuple containing start and end time of the spike
    :param unit_ms: use ms as unit for times in t_lim and resulting events
    :returns: numpy array containing spike times in s (or ms, if unit_ms is set)
    """

    assert len(t_lim) == 2

    if unit_ms:
        t_lim = (t_lim[0] / 1000, t_lim[1] / 1000)

    if rate > 0.:
        events_ = [t_lim[0]]

        while events_[-1] < t_lim[1]:
            T = t_lim[1] - events_[-1]

            # expected number of events
            num_expected = T * rate

            # number of events to generate
            num_generate = np.ceil(num_expected + 3 * np.sqrt(num_expected))
            num_generate = int(max(num_generate, 1000))

            beta = 1. / rate
            isi_ = np.random.exponential(beta, size=num_generate)
            newevents_ = np.cumsum(isi_) + events_[-1]
            events_ = np.append(events_, newevents_)

        lastind = np.searchsorted(events_, t_lim[1])
        events_ = events_[1:lastind]  # drop ghost spike at start

        if unit_ms:
            events_ *= 1000.

    elif rate == 0.:
        events_ = np.asarray([])

    else:
        raise ValueError('requested negative rate.')

    return events_

def generate_stimulus(t_sim, stim_len=50, stim_dt=500, num_input=3, rate=200, dt=.1):
    """
    Generate input spikes.

    :param t_sim: total time for stimulus generation in ms
    :param stim_len: duration of each stimulus
    :param stim_dt: stimulus spacing
    :param num_input: number of input signals (i.e. number of input neurons)
    :param rate: firing rate of active neurons in Hz
    :param dt: simulation time step for rounding
    :returns: list contain a list of spike times for each input neuron
    """

    num_stim = int(np.floor(t_sim / stim_dt) - 1)
    bits = np.random.randint(2, size=(num_stim, num_input))

    t_stim_ = stim_dt * np.arange(1, num_stim + 1)
    assert len(t_stim_) == bits.shape[0]

    spikes = [np.array([]) for n in range(num_input)]

    for n in range(num_input):
        for t, bit in zip(t_stim_, bits[:,n]):
            if bit == 1:
                spikes[n] = np.append(spikes[n], poisson_generator(rate, t_lim=(t, t + stim_len), unit_ms=True))

    # round to dt, clip, sort out duplicates
    spikes = [np.round(sp / dt).astype(int) for sp in spikes]
    spikes = [np.clip(sp, 1, t_sim / dt) for sp in spikes]
    spikes = [np.unique(sp) * dt for sp in spikes]

    # remove possible duplicates

    # brian data format
    ids = np.concatenate([k * np.ones(len(sp), dtype=int) for k, sp in enumerate(spikes)])
    times = np.concatenate(spikes)
    assert len(times) == len(ids)

    return bits, spikes, ids, times


#%%definitions
def truncnorm(
    mu:float=0, sigma:float=1,
    xmin:float=None, xmax:float=None,
    size:tuple=1,
    ) -> np.ndarray:
    """returns samples from truncated normal distribution
    
    - function to generate samples from a truncated normal distribution

    Parameters
        - mu
            - float, optional
            - mean
            - the default is 0
        - sigma
            - float, optional
            - standard deviation
            - the default is 1
        - xmin
            - float, optional
            - lower truncation bound
            - the default is None
                - no trunctation
        - xmax
            - float, optional
            - upper truncation bound
            - the default is None
                - no trunctation
        - size
            - tuple, optional
            - shape of the array to generate
            - the default is 1
        - verbose
            - int, optional
            - verbosity level
            - the default is 0

    Returns
        - out
            - np.ndarray
            - samples drawn from a truncated normal distribution
    """
    
    if xmin is None: xmin = -np.inf
    if xmax is None: xmax = np.inf
    #draw initial distribution
    out = np.random.normal(mu, sigma, size=size)
    
    #correct wrong values
    oob = np.array(np.where((out < xmin)|(xmax < out))).T   #out of bounds
    for idx in oob:
        while (out[tuple(idx)] < xmin) or (xmax < out[tuple(idx)]):
            out[tuple(idx)] = np.random.normal(mu, sigma, size=1)
        
    return out

def lif_ng(
    n:int,
    u_rest, u_reset, u_th,
    R_m, tau_m,
    delta_abs,
    tau_syn,
    u0=None,
    ) -> NeuronGroup:
    """returns generated LIF neuron group
    """

    eqs = """
    du_m/dt = ( -(u_m - u_rest) + R_m * I) / tau_m : volt (unless refractory)
    dI/dt = -I / tau_syn : ampere
    """

    u0 = u_rest if u0 is None else u0
    thres = "u_m >= u_th"
    reset = "u_m = u_reset"

    neurons = NeuronGroup(n,
        eqs,
        threshold=thres,
        reset=reset,
        refractory=delta_abs,
        method="exact",
        namespace=dict(
            u_rest=u_rest, u_reset=u_reset, u_th=u_th,
            R_m=R_m, tau_m=tau_m,
            delta_abs=delta_abs,
            tau_syn=tau_syn,
        ),
    )
    neurons.u_m = u0

    return neurons

def stp_syn(
    ng_pre:NeuronGroup, ng_post:NeuronGroup,
    w_mean, w_std, w_min, w_max,
    delay:str, U,
    tau_fac, tau_rec,
    connect_i:Any=None, connect_j:Any=None,
    ) -> Synapses:

    syn_eqs = """
        w : ampere                              #weight efficacy
        U : 1
        tau_fac : second
        tau_rec : second
        du/dt = -u/tau_fac  : 1 (event-driven)  #active
        dz/dt = -z/tau_rec  : 1 (event-driven)  #recovered
        R = 1 - z           : 1                 #update R
    """

    on_pre = """
        u += U*(1-u)            #update u first! u- (before update)
        z += R*u                #R- (before update), u+ (after update)
        I_post += w*u*R         #update current. u+ (after update), R- (before update)
    """

    syn = Synapses(
        ng_pre, ng_post,
        on_pre=on_pre, model=syn_eqs,
    )

    syn.connect(
        i=connect_i,
        j=connect_j,
    )

    syn.w = truncnorm(mu=w_mean, sigma=w_std*abs(w_mean), xmin=w_min, xmax=w_max, size=(len(syn.i))) *pA
    syn.delay = delay
    syn.U = U
    syn.tau_fac = tau_fac
    syn.tau_rec = tau_rec
    
    return syn

def experiment():

    t_sim = 120 * second
    dt = .1 * ms

    N_E = 5 #1000
    N_I = 5 #250
    n_in = 3

    stim_len = 50
    stim_dt = 250

    #setup brian2
    brian2.defaultclock.dt = dt
    net = brian2.Network()

    #init neurons
    ##lsm pools
    ng_E = lif_ng(N_E,    #excitatory
        u_rest=-65*mV, u_reset=-72*mV, u_th=-60*mV,
        R_m=(30*ms)/(30*pF), tau_m=30*ms,
        delta_abs=3*ms,
        tau_syn=5*ms,
    )
    ng_I = lif_ng(N_I,    #inhibitory
        u_rest=-65*mV, u_reset=-72*mV, u_th=-60*mV,
        R_m=(30*ms)/(30*pF), tau_m=30*ms,
        delta_abs=3*ms,
        tau_syn=5*ms,
    )
    local_logger.debug(ng_E)
    local_logger.debug(ng_I)

    ##stimulus (input neuron)
    input_bits, stim_spike_trains, stim_ids, stim_times = generate_stimulus(t_sim / ms, stim_len=stim_len, stim_dt=stim_dt, num_input=n_in, dt=dt/ms)
    num_input = input_bits.shape[1]
    ng_in = SpikeGeneratorGroup(n_in, stim_ids, stim_times*ms)

    ##background noise input
    poisson_input_E = PoissonInput(ng_E, 'I', 1, 25*Hz, weight=5*pA)
    poisson_input_I = PoissonInput(ng_I, 'I', 1, 25*Hz, weight=5*pA)

    #wiring
    C_inE = 200  #outgoing
    syn_inE = stp_syn(ng_in, ng_E,
        w_mean=660, w_std=0.7, w_min=0, w_max=None,
        delay="50*ms + 80*ms*rand()",
        U=0.44,
        tau_fac=12*ms, tau_rec=223*ms,
        connect_i=np.concatenate([[i_pre]*C_inE for i_pre in range(ng_in.N)]),
        connect_j=np.random.randint(0, ng_E.N, size=C_inE*ng_in.N),
    )
    C_EE = 2    #incoming
    syn_EE = stp_syn(ng_E, ng_E,
        w_mean=205, w_std=0.7, w_min=0, w_max=None,
        delay="50*ms + 80*ms*rand()",
        U=0.59,
        tau_fac=1*ms, tau_rec=813*ms,
        connect_i=np.random.randint(0, ng_E.N, size=C_EE*ng_E.N),
        connect_j=np.concatenate([[i_post]*C_EE for i_post in range(ng_E.N)])
    )
    C_EI = 2    #incoming
    syn_EI = stp_syn(ng_E, ng_I,
        w_mean=95, w_std=0.7, w_min=0, w_max=None,
        delay="8*ms + 10*ms*rand()",
        U=0.049,
        tau_fac=1790*ms, tau_rec=399*ms,
        connect_i=np.random.randint(0, ng_E.N, size=C_EI*ng_I.N),
        connect_j=np.concatenate([[i_post]*C_EI for i_post in range(ng_I.N)])
    )
    C_IE = 2    #incoming
    syn_IE = stp_syn(ng_I, ng_E,
        w_mean=-450, w_std=0.7, w_min=None, w_max=0,
        delay="8*ms + 10*ms*rand()",
        U=0.016,
        tau_fac=376*ms, tau_rec=45*ms,
        connect_i=np.random.randint(0, ng_I.N, size=C_IE*ng_E.N),
        connect_j=np.concatenate([[i_post]*C_IE for i_post in range(ng_E.N)])
    )
    C_II = 2    #incoming
    syn_II = stp_syn(ng_I, ng_I,
        w_mean=-370, w_std=0.7, w_min=None, w_max=0,
        delay="8*ms + 10*ms*rand()",
        U=0.25,
        tau_fac=21*ms, tau_rec=706*ms,                     
        connect_i=np.random.randint(0, ng_I.N, size=C_II*ng_I.N),
        connect_j=np.concatenate([[i_post]*C_II for i_post in range(ng_I.N)])
    )    

    #monitoring
    spike_mon_E = SpikeMonitor(ng_E)
    spike_mon_I = SpikeMonitor(ng_I)
    spike_mon_in = SpikeMonitor(ng_in)

    #add to network
    units = [
        ng_E, ng_I,
        poisson_input_E, poisson_input_I,
        spike_mon_E, spike_mon_I, spike_mon_in, 
        syn_inE, syn_EE, syn_EI, syn_IE, syn_II,
    ]
    net.add(units)
    local_logger.debug(net)

    # #simulate
    # net.run(t_sim, report='stdout', report_period=10 * second)


    return


#%%main
def main():
    experiment()
    return

if __name__ == "__main__":
    main()
