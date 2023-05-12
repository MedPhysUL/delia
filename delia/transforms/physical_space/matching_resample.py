"""
    @file:              matching_resample.py
    @Author:            Maxence Larose

    @Creation Date:     03/2022
    @Last modification: 03/2022

    @Description:       This file contains the MatchingResampled transform.
"""

from typing import Callable, Dict, Hashable

import SimpleITK as sitk

from delia.transforms.physical_space.transform import PhysicalSpaceTransform, ImageData, KeysCollection, Mode


class MatchingResampled(PhysicalSpaceTransform):
    """
    Resample matching images to the spacing, size, origin and direction of a given reference image.
    """

    def __init__(
            self,
            reference_image_key: str,
            matching_keys: KeysCollection,
            interpolator: Callable = sitk.sitkBSpline,
    ):
        """
        Initializes images.

        Parameters
        ----------
        reference_image_key : str
            Key of the image from which the spacing, size, origin and direction are taken.
        matching_keys : KeysCollection
            Keys of the corresponding items to be transformed using the calculated coordinates of spatial bounding box
            for foreground on the image. Image keys are assumed to be arbitrary series keys defined in
            'series_descriptions'. For the label maps, the keys are organ names. Note that if 'series_descriptions' is
            None, the image keys are assumed to be modality names.
        interpolator : Callable
            The interpolator to be used for resampling the images. Default = sitk.sitkBSpline.
        """
        keys = [key for key in matching_keys] + [reference_image_key]
        super().__init__(keys=keys)
        self._reference_image_key = reference_image_key
        self._interpolator = interpolator

    def __call__(self, data: Dict[str, ImageData]) -> Dict[Hashable, sitk.Image]:
        """
        Resamples matching itk images to the spacing, size, origin and direction of a given reference image.

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

        reference_image = None
        for key in self.key_iterator(d):
            if key == self._reference_image_key:
                reference_image = d[key].simple_itk_image

        for key in self.key_iterator(d):
            if key != self._reference_image_key:

                if self._mode == Mode.NONE:
                    raise AssertionError("Transform mode must be set before __call__.")
                elif self._mode == Mode.IMAGE:
                    interpolator = self._interpolator
                elif self._mode == Mode.SEGMENTATION:
                    interpolator = sitk.sitkNearestNeighbor
                else:
                    raise ValueError("Unknown transform mode.")

                d[key] = sitk.Resample(
                    image1=d[key].simple_itk_image,
                    referenceImage=reference_image,
                    interpolator=interpolator
                )

        return d


MatchingResampleD = MatchingResampleDict = MatchingResampled
