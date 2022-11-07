"""
    @file:              resample.py
    @Author:            Maxence Larose

    @Creation Date:     10/2022
    @Last modification: 11/2022

    @Description:       This file contains the Resampled transform.
"""

from typing import Dict, Hashable, Tuple

import SimpleITK as sitk
import numpy as np

from dicom2hdf.transforms.physical_space.transform import PhysicalSpaceTransform, ImageData, KeysCollection, Mode


class Resampled(PhysicalSpaceTransform):
    """
    Resample an itk_image to new out_spacing.
    """

    def __init__(
            self,
            keys: KeysCollection,
            out_spacing: Tuple[float, float, float] = (1.0, 1.0, 1.0)
    ):
        """
        Initialize output spacing.

        Parameters
        ----------
        keys : KeysCollection
            Keys of the corresponding items to be transformed. Image keys are assumed to be arbitrary series keys
            defined in 'series_descriptions'. For the label maps, the keys are organ names. Note that if
            'series_descriptions' is None, the image keys are assumed to be modality names.
        out_spacing : Tuple[int, int, int], default = (1.0, 1.0, 1.0)
            The desired spacing in the physical space. Default = (1.0 mm, 1.0 mm, 1.0 mm).
        """
        super().__init__(keys=keys)
        self._out_spacing = out_spacing

    def __call__(self, data: Dict[str, ImageData]) -> Dict[Hashable, sitk.Image]:
        """
        Resample an itk_image to new out_spacing.

        Parameters
        ----------
        data : Dict[str, ImageData]
            A Python dictionary that contains ImageData.

        Returns
        -------
        transformed_image : Dict[Hashable, sitk.Image]
            A Python dictionary that contains transformed SimpleITK images.
        """
        d = dict(data)

        for key in self.key_iterator(d):
            original_itk_image = d[key].simple_itk_image

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

            if self._mode == Mode.NONE:
                raise AssertionError("Transform mode must be set before __call__.")
            elif self._mode == Mode.IMAGE:
                resample.SetInterpolator(sitk.sitkLinear)
            elif self._mode == Mode.SEGMENTATION:
                resample.SetInterpolator(sitk.sitkNearestNeighbor)
            else:
                raise ValueError("Unknown transform mode.")

            resampled_image = resample.Execute(original_itk_image)

            d[key] = resampled_image

        return d


ResampleD = ResampleDict = Resampled
