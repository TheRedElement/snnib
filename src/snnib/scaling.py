"""functions for scaling data

Exceptions

Classes

Functions
    - `minmaxscale()` -- scale data to some target range

Other Objects
"""

#%%imports
import numpy as np

#%%definitions
def minmaxscale(x:np.ndarray,
    xmin:float=0.0, xmax:float=1.0,
    xmin_ref:float=None, xmax_ref:float=None,
    axis:int=None,
    ):
    """returns minmax scaled version of `x` along `axis`

    Parameters
        - `x`
            - `np.ndarray`
            - array to be scaled
        - `xmin`
            - `float`, optional
            - minimum of the target range
            - the default is `0.0`
        - `xmax`
            - `float`, optional
            - maximum of the target range
            - the default is `1.0`
        - `xmin_ref`
            - `float`, optional
            - minimum of the source
                - the range that `x` belongs to
            - the default is `None`
                - will be set to `np.min(x, axis=axis)
        - `xmax_ref`
            - `float`, optional
            - maximum of the source
                - the range that `x` belongs to
            - the default is `None`
                - will be set to `np.max(x, axis=axis)
        - `axis`
            - `int`, optional
            - axis onto which to apply minmaxscaling
            - the default is `None`
                - applied to whole array

    Raises

    Returns
        - `x_s`
            - `np.ndarray`
            - same shape as `x`
            - scaled version of `x`

    Dependencies
        - `numpy`
    """
    xmin_ref = np.min(x, axis=axis) if xmin_ref is None else xmin_ref
    xmax_ref = np.max(x, axis=axis) if xmax_ref is None else xmax_ref

    x_s = (x - xmin_ref)/(xmax_ref - xmin_ref) * (xmax - xmin) + xmin

    return x_s

