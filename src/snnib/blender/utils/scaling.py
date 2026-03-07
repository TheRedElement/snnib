"""
"""

#%%imports
import numpy as np

#%%definitions
def minmaxscale(x,
    xmin=0, xmax=1,
    xmin_ref=None, xmax_ref=None,
    axis=None,
    ):
    """returns minmax scaled version of `x`
    """
    xmin_ref = np.min(x, axis=axis) if xmin_ref is None else xmin_ref
    xmax_ref = np.max(x, axis=axis) if xmax_ref is None else xmax_ref

    x_s = (x - xmin_ref)/(xmax_ref - xmin_ref) * (xmax - xmin) + xmin

    return x_s


#%%registration
def register():
    pass
def unregister():
    pass