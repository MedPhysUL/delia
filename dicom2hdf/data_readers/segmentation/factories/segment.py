"""
    @file:              segment.py
    @Author:            Maxence Larose

    @Creation Date:     12/2021
    @Last modification: 12/2021

    @Description:       This file contains the Segment class.
"""

import numpy as np
import SimpleITK as sitk


class Segment:
    """
    A class used to represent a segment object.
    """

    def __init__(self, name: str, simple_itk_label_map: np.ndarray):
        """
        Constructor of the segment object.

        Parameters
        ----------
        name : str
            Segment's name.
        simple_itk_label_map : sitk.Image
            The segmentation as a SimpleITK image.
        """
        self._name = name
        self._simple_itk_label_map = simple_itk_label_map

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
    def simple_itk_label_map(self) -> sitk.Image:
        """
        Simple ITK label map image.

        Returns
        -------
        simple_itk_label_map : sitk.Image
            The segmentation as a SimpleITK image.
        """
        return self._simple_itk_label_map
