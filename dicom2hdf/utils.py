"""
    @file:              utils.py
    @Author:            Maxence Larose

    @Creation Date:     10/2021
    @Last modification: 03/2022

    @Description:       A collection of functions and classes that may or may not be useful.
"""

import os
from typing import Callable
import warnings


def is_path_valid(
        path: str
) -> None:
    """
    Raise a ValueError if the given path doesn't exist.

    Parameters
    ----------
    path : str
        A path.

    Returns
    -------
    None
    """
    if not os.path.exists(path):
        raise FileNotFoundError(f"Given path {path} does not exist.")


class Decorators:

    @classmethod
    def deprecated(cls, explanation: str) -> Callable:
        """
        Decorator to use on deprecated functions.

        Parameters
        ----------
        explanation : str
            Explanation of depreciation and recommended alternative function.

        Returns
        -------
        deprecated_func: Callable
            Deprecated function.
        """
        def deprecated_func(func):
            def wrapper(*args, **kwargs):
                warnings.warn(explanation, DeprecationWarning)
                return func(*args, **kwargs)

            return wrapper

        return deprecated_func
