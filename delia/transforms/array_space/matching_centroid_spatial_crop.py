"""
    @file:              matching_centroid_spatial_crop.py
    @Author:            Maxence Larose

    @Creation Date:     03/2023
    @Last modification: 03/2023

    @Description:       This file contains the MatchingCentroidSpatialCropd transform.
"""

from typing import Collection, Dict, Hashable, Sequence, Union
from warnings import warn

from monai.transforms import SpatialCrop
import numpy as np

from .tools import compute_centroid
from ..tools import Mode
from .transform import ArraySpaceTransform

KeysCollection = Union[Collection[Hashable], Hashable]


class MatchingCentroidSpatialCropd(ArraySpaceTransform):
    """
    Performs crop around the centroid of a segmentation, get the used coordinates of the spatial bounding box and apply
    this crop on other matching images.
    """

    def __init__(
            self,
            segmentation_key: str,
            matching_keys: KeysCollection,
            roi_size: Union[Sequence[int], int]
    ):
        """
        Initializes output spacing.

        Parameters
        ----------
        segmentation_key : str
            Key of the segmentation from which to crop around the centroid and to get coordinates of the spatial
            bounding box. Segmentation keys are organ names.
        matching_keys : KeysCollection
            Keys of the corresponding items to be transformed using the calculated coordinates of the spatial bounding
            box around the centroid of the segmentation. Image keys are assumed to be arbitrary series keys defined in
            'series_descriptions'. For the label maps, the keys are organ names. Note that if 'series_descriptions' is
            None, the image keys are assumed to be modality names.
        roi_size : Union[Sequence[int], int]
            The size of the crop region e.g. [224,224,128]. If a dimension of ROI size is larger than image size, will
            not crop that dimension of the image. If its components have non-positive values, the corresponding size of
            input image will be used. For example: if the spatial size of input data is [40, 40, 40] and
            `roi_size=[32, 64, -1]`, the spatial size of output data will be [32, 40, 40].
        """
        keys = [key for key in matching_keys] + [segmentation_key]
        super().__init__(keys=keys)

        self._centroid = None
        self._segmentation_key = segmentation_key
        self._roi_size = roi_size

    def __call__(self, data: Dict[Hashable, np.ndarray]) -> Dict[str, np.ndarray]:
        """
        Performs crop around the centroid of a segmentation, get the used coordinates of the spatial bounding box and
        apply this crop on other matching images.

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

        if self._mode == Mode.NONE:
            raise AssertionError("Transform mode must be set before __call__.")
        elif self._mode == Mode.IMAGE:
            assert self._centroid is not None, "'centroid' must be set before __call__ with image mode."
        elif self._mode == Mode.SEGMENTATION:
            self._centroid = compute_centroid(d[self._segmentation_key])
        else:
            raise ValueError("Unknown transform mode.")

        spatial_crop = SpatialCrop(roi_center=self._centroid, roi_size=self._roi_size)

        for key in self.key_iterator(d):
            if key == self._segmentation_key:
                n_original_voxels = (d[key] == 1).sum().item()
                d[key] = spatial_crop(d[key])
                n_final_voxels = (d[key] == 1).sum().item()

                if n_original_voxels != n_final_voxels:
                    warn(
                        f"The matching centroid spatial crop bounding box doesn't contain all the '1' voxels of the "
                        f"orignal label map. The total number of voxels in the original label map was "
                        f"{n_original_voxels} and the total number of voxels in the cropped label map is "
                        f"{n_final_voxels}. The difference (in voxels) is {n_original_voxels - n_final_voxels}."
                    )
            else:
                d[key] = spatial_crop(d[key])

        if self._mode == Mode.IMAGE:
            self._centroid = None

        return d


MatchingCentroidSpatialCropD = MatchingCentroidSpatialCropDict = MatchingCentroidSpatialCropd
