"""
    @file:              tools.py
    @Author:            Maxence Larose

    @Creation Date:     03/2023
    @Last modification: 03/2023

    @Description:       This file contains some tools to help applying array space transforms on images.
"""

from typing import Tuple, Union

import numpy as np
from monai.data import MetaTensor

from ..tools import convert_to_numpy


def compute_centroid(array: Union[MetaTensor, np.ndarray]) -> Tuple[int, int, int]:
    """
    Computes centroid.

    Parameters
    ----------
    array : Union[MetaTensor, np.ndarray]
        Image tensor or array.

    Returns
    -------
    centroid : Tuple[int, int, int]
        Centroid.
    """
    np_array = convert_to_numpy(array)
    assert np.array_equal(np_array, np_array.astype(bool)), (
        "The array to compute the centroid on must be a binary numpy array."
    )
    binary_array = (np_array == 1)
    centroid = np.argwhere(binary_array).sum(0)/binary_array.sum()

    return centroid.astype(int)
