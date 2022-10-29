"""
    @file:              transforms.py
    @Author:            Maxence Larose

    @Creation Date:     10/2022
    @Last modification: 10/2022

    @Description:       This file contains the BaseTransform abstract class which is used to define transforms that can
                        be applied to images and segmentations.
"""

from abc import abstractmethod
from typing import Collection, Dict, Hashable, Mapping, Tuple, Union

import SimpleITK as sitk
from monai.transforms.transform import MapTransform
import numpy as np

KeysCollection = Union[Collection[Hashable], Hashable]


class PhysicalSpaceTransform(MapTransform):
    """
    Base transform abstract class.
    """

    def __init__(self, keys: KeysCollection, allow_missing_keys: bool = True) -> None:
        """
        Initialize transform keys.

        Parameters
        ----------
        keys : KeysCollection
            Keys of the corresponding items to be transformed. Keys are assumed to be modality names for images and
            organ names for segmentations.
        allow_missing_keys : bool
            Don't raise exception if key is missing.
        """
        super().__init__(keys=keys, allow_missing_keys=allow_missing_keys)

    @abstractmethod
    def __call__(self, data: Mapping[Hashable, sitk.Image]) -> Dict[Hashable, sitk.Image]:
        """
        Apply the transformation.

        Parameters
        ----------
        data : Mapping[Hashable, sitk.Image]
            A Python dictionary that contains SimpleITK images.

        Returns
        -------
        transformed_data : Dict[Hashable, sitk.Image]
            A Python dictionary that contains transformed SimpleITK images.
        """
        raise NotImplementedError


class ResampleD(PhysicalSpaceTransform):
    """
    Resample an itk_image to new out_spacing.
    """

    def __init__(
            self,
            keys: KeysCollection,
            segmentation: bool,
            out_spacing: Tuple[float, float, float] = (1.0, 1.0, 1.0),
            allow_missing_keys: bool = True
    ):
        """
        Initialize output spacing.

        Parameters
        ----------
        keys : KeysCollection
            Keys of the corresponding items to be transformed.
        segmentation : bool
            Whether the simple ITK images are segmentations or not. This parameter will change the interpolator used
            during resampling.
        out_spacing : Tuple[int, int, int], default = (1.0, 1.0, 1.0)
            The desired spacing in the physical space. Default = (1.0 mm, 1.0 mm, 1.0 mm).
        allow_missing_keys : bool
            Don't raise exception if key is missing.
        """
        super().__init__(keys=keys, allow_missing_keys=allow_missing_keys)
        self._out_spacing = out_spacing
        self._segmentation = segmentation

    def __call__(self, data: Mapping[Hashable, sitk.Image]) -> Dict[Hashable, sitk.Image]:
        """
        Resample an itk_image to new out_spacing.

        Parameters
        ----------
        data : Mapping[Hashable, sitk.Image]
            A Python dictionary that contains SimpleITK images.

        Returns
        -------
        transformed_image : Dict[Hashable, sitk.Image]
            A Python dictionary that contains transformed SimpleITK images.
        """
        d = dict(data)

        for key in self.key_iterator(d):
            original_itk_image = d[key]

            original_spacing = original_itk_image.GetSpacing()
            original_size = original_itk_image.GetSize()

            out_size = [
                int(np.round(original_size[0] * (original_spacing[0] / self._out_spacing[0]))),
                int(np.round(original_size[1] * (original_spacing[1] / self._out_spacing[1]))),
                int(np.round(original_size[2] * (original_spacing[2] / self._out_spacing[2])))
            ]

            resample = sitk.ResampleImageFilter()
            resample.SetOutputSpacing(self._out_spacing)
            resample.SetSize(out_size)
            resample.SetOutputDirection(original_itk_image.GetDirection())
            resample.SetOutputOrigin(original_itk_image.GetOrigin())
            resample.SetTransform(sitk.Transform())
            resample.SetDefaultPixelValue(original_itk_image.GetPixelIDValue())

            if self._segmentation:
                resample.SetInterpolator(sitk.sitkNearestNeighbor)
            else:
                resample.SetInterpolator(sitk.sitkLinear)

            resampled_image = resample.Execute(original_itk_image)

            d[key] = resampled_image

        return d


class ResampleImageD(ResampleD):
    """
    Resample an itk_image to new out_spacing.
    """

    def __init__(
            self,
            keys: KeysCollection,
            out_spacing: Tuple[float, float, float] = (1.0, 1.0, 1.0),
            allow_missing_keys: bool = True
    ):
        """
        Initialize output spacing.

        Parameters
        ----------
        keys : KeysCollection
            Keys of the corresponding items to be transformed. Keys are assumed to be modality names.
        out_spacing : Tuple[int, int, int], default = (1.0, 1.0, 1.0)
            The desired spacing in the physical space. Default = (1.0 mm, 1.0 mm, 1.0 mm).
        allow_missing_keys : bool
            Don't raise exception if key is missing.
        """
        super().__init__(keys=keys, segmentation=False, allow_missing_keys=allow_missing_keys, out_spacing=out_spacing)


class ResampleSegmentationD(ResampleD):
    """
    Resample an itk_image representing a segmentation to a new out_spacing.
    """

    def __init__(
            self,
            keys: KeysCollection,
            out_spacing: Tuple[float, float, float] = (1.0, 1.0, 1.0),
            allow_missing_keys: bool = True
    ):
        """
        Initialize output spacing.

        Parameters
        ----------
        keys : KeysCollection
            Keys of the corresponding items to be transformed. Keys are assumed to be organ names.
        out_spacing : Tuple[int, int, int], default = (1.0, 1.0, 1.0)
            The desired spacing in the physical space. Default = (1.0 mm, 1.0 mm, 1.0 mm).
        allow_missing_keys : bool
            Don't raise exception if key is missing.
        """
        super().__init__(keys=keys, segmentation=True, allow_missing_keys=allow_missing_keys, out_spacing=out_spacing)
