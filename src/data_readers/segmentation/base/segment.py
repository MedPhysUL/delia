"""
    @file:              segment.py
    @Author:            Maxence Larose

    @Creation Date:     12/2021
    @Last modification: 12/2021

    @Description:       This file contains the Segment class.
"""

import numpy as np


class Segment:
    """
    A class used to represent a segment object.
    """

    def __init__(self, name: str, label_map: np.ndarray):
        """
        Constructor of the segment object.

        Parameters
        ----------
        name : str
            Segment's name.
        label_map : np.ndarray
            A binary label map with the same size as the original image.
        """
        self._name = name
        self._label_map = label_map

    @property
    def name(self) -> str:
        """
        Name property.

        Returns
        -------
        name : str
            Segment's name.
        """
        return self._name

    @property
    def label_map(self) -> np.ndarray:
        """
        Label map property.

        Returns
        -------
        label_map : np.ndarray
            A binary label map with the same size as the original image.
        """
        return self._label_map
