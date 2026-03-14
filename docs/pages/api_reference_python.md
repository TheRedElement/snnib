<!-- NOTE: :recursive: -> show all children as well (to display all methods when summarizing class) -->


# API Reference (Python Package)

```{eval-rst}
.. currentmodule:: snnib.blender
```

## snnib

```{eval-rst}
.. autosummary::
    :signatures: short
    :recursive:
    :toctree: tocSnnib/

    brian2_utils.get_spike_monitor
    
```


## snnib.simulations

```{eval-rst}
.. autosummary::
    :signatures: short
    :recursive:
    :toctree: tocSimulations/

    simulations
    simulation.brian2_simulation.experiment()
```




## Backends

### [matplotlib](https://matplotlib.org/)

```{eval-rst}
.. autosummary::
    :signatures: none
    :recursive:
    :toctree: tocMPL/

    LSteinMPL
    LSteinMPL.__init__
    LSteinMPL.add_thetaaxis
    LSteinMPL.add_xaxis
    LSteinMPL.add_yaxis
    LSteinMPL.add_ylabel
    LSteinMPL.show
```

### [Plotly](https://plotly.com/python/)

```{eval-rst}
.. autosummary::
    :signatures: none
    :recursive:
    :toctree: tocPlotly/

    LSteinPlotly
    LSteinPlotly.__init__
    LSteinPlotly.add_thetaaxis
    LSteinPlotly.add_xaxis
    LSteinPlotly.add_yaxis
    LSteinPlotly.add_ylabel
    LSteinPlotly.show
    LSteinPlotly.translate_kwargs
```

## Utils
```{eval-rst}
.. currentmodule:: lstein
```

```{eval-rst}
.. autosummary::
    :signatures: none
    :recursive:
    :toctree: tocUtils/

    utils.cart2polar
    utils.correct_labelrotation
    utils.get_colors
    utils.minmaxscale
    utils.polar2cart
```