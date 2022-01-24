"""
    @file:              utils.py
    @Author:            Maxence Larose

    @Creation Date:     10/2021
    @Last modification: 01/2022

    @Description:       A collection of functions and classes that may or may not be useful.
"""

import os
import enum
from typing import Callable, Union
import warnings


def check_validity_of_given_path(
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


def check_validity_of_given_name(name: str, enum_class: Union[enum.Enum, enum.IntEnum]) -> None:
    """
    Raise a ValueError if the given anatomical plane is not a member of the AnatomicalPlane Enum Class.

    Parameters
    ----------
    name : str
        Name.
    enum_class : Union[enum.Enum, enum.IntEnum]
        Class inheriting from enum.Enum or enum.IntEnum.

    Returns
    -------
    None
    """
    if name in enum_class.__members__:
        pass
    else:
        raise ValueError(f"Given member {name} doesn't exist. Allowed members of {enum_class} are "
                         f"{list(enum_class.__members__)}.")


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
