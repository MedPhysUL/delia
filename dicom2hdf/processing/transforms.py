"""
    @file:              transforms.py
    @Author:            Maxence Larose

    @Creation Date:     05/2022
    @Last modification: 05/2022

    @Description:       This file contains the BaseTransform abstract class which is used to define transforms that can
                        be applied to images and segmentations.
"""

from abc import ABC, abstractmethod
from typing import Tuple

import SimpleITK as sitk
import numpy as np


class BaseTransform(ABC):
    """
    Base transform abstract class.
    """

    @abstractmethod
    def forward(self, itk_image: sitk.Image, segmentation: bool = False) -> sitk.Image:
        """
        Apply the transformation.

        Parameters
        ----------
        itk_image : sitk.Image
            The input image.
        segmentation : bool
            Whether the simple ITK image is a segmentation or not.

        Returns
        -------
        resampled_image : sitk.Image
            The resampled image.
        """
        raise NotImplementedError


class Resample(BaseTransform):
    """
    Resample an itk_image to new out_spacing.
    """

    def __init__(self, out_spacing: Tuple[float, float, float] = (1.0, 1.0, 1.0)):
        """
        Initialize output spacing.

        Parameters
        ----------
        out_spacing : Tuple[int, int, int], default = (1.0, 1.0, 1.0)
            The desired spacing.
        """
        super(Resample).__init__()
        self._out_spacing = out_spacing

    def forward(self, itk_image: sitk.Image, segmentation: bool = False) -> sitk.Image:
        """
        Resample an itk_image to new out_spacing.

        Parameters
        ----------
        itk_image : sitk.Image
            The input image.
        segmentation : bool
            Whether the simple ITK image is a segmentation or not. This parameter will change the interpolator used
            during resampling.

        Returns
        -------
        resampled_image : sitk.Image
            The resampled image.
        """
        original_spacing = itk_image.GetSpacing()
        original_size = itk_image.GetSize()

        out_size = [
            int(np.round(original_size[0] * (original_spacing[0] / self._out_spacing[0]))),
            int(np.round(original_size[1] * (original_spacing[1] / self._out_spacing[1]))),
            int(np.round(original_size[2] * (original_spacing[2] / self._out_spacing[2])))
        ]

        resample = sitk.ResampleImageFilter()
        resample.SetOutputSpacing(self._out_spacing)
        resample.SetSize(out_size)
        resample.SetOutputDirection(itk_image.GetDirection())
        resample.SetOutputOrigin(itk_image.GetOrigin())
        resample.SetTransform(sitk.Transform())
        resample.SetDefaultPixelValue(itk_image.GetPixelIDValue())

        if segmentation:
            resample.SetInterpolator(sitk.sitkNearestNeighbor)
        else:
            resample.SetInterpolator(sitk.sitkLinear)

        resampled_image = resample.Execute(itk_image)

        return resampled_image
