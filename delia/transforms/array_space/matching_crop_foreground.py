"""
    @file:              matching_crop_foreground.py
    @Author:            Maxence Larose

    @Creation Date:     11/2022
    @Last modification: 11/2022

    @Description:       This file contains the MatchingCropForeground transform.
"""

from typing import Collection, Dict, Hashable, Union

from monai.transforms import CropForeground, SpatialCrop
import numpy as np

from .transform import ArraySpaceTransform

KeysCollection = Union[Collection[Hashable], Hashable]


class MatchingCropForegroundd(ArraySpaceTransform):
    """
    Performs CropForeground on an image, get the used coordinates of spatial bounding box for foreground and apply this
    crop on other matching images.
    """

    def __init__(
            self,
            reference_image_key: str,
            matching_keys: KeysCollection,
    ):
        """
        Initialize output spacing.

        Parameters
        ----------
        reference_image_key : str
            Key of the image from which to crop foreground and to get coordinates of spatial bounding box for
            foreground. Image keys are assumed to be arbitrary series keys defined in 'series_descriptions'. Note that
            if 'series_descriptions' is None, the image keys are assumed to be modality names.
        matching_keys : KeysCollection
            Keys of the corresponding items to be transformed using the calculated coordinates of spatial bounding box
            for foreground on the image. Image keys are assumed to be arbitrary series keys defined in
            'series_descriptions'. For the label maps, the keys are organ names. Note that if 'series_descriptions' is
            None, the image keys are assumed to be modality names.
        """
        keys = [key for key in matching_keys] + [reference_image_key]
        super().__init__(keys=keys)

        self._reference_image_key = reference_image_key
        self._crop_foreground = CropForeground(return_coords=True)

    def __call__(self, data: Dict[Hashable, np.ndarray]) -> Dict[str, np.ndarray]:
        """
        Performs CropForeground on an image, get the used coordinates of spatial bounding box for foreground and apply
        this crop on other matching images.

        Parameters
        ----------
        data : Dict[Hashable, np.ndarray]
            A Python dictionary that contains numpy ndarray.

        Returns
        -------
        transformed_data : Dict[Hashable, np.ndarray]
            A Python dictionary that contains transformed numpy ndarray.
        """
        d = dict(data)

        start, end = None, None
        for key in self.key_iterator(d):
            if key == self._reference_image_key:
                d[key], start, end = self._crop_foreground(d[key])

        spatial_crop = SpatialCrop(roi_start=start, roi_end=end)

        for key in self.key_iterator(d):
            if key != self._reference_image_key:
                d[key] = spatial_crop(d[key])

        return d


MatchingCropForegroundD = MatchingCropForegroundDict = MatchingCropForegroundd
