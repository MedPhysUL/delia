"""
    @file:              transform.py
    @Author:            Maxence Larose

    @Creation Date:     10/2022
    @Last modification: 11/2022

    @Description:       This file contains the PhysicalSpaceTransform abstract class which is used to define transforms
                        that can be applied to images and segmentations.
"""

from abc import abstractmethod
from typing import Collection, Dict, Hashable, NamedTuple, Union

import SimpleITK as sitk
import pydicom
from monai.transforms import MapTransform

from ..tools import Mode

KeysCollection = Union[Collection[Hashable], Hashable]


class ImageData(NamedTuple):
    """
    A named tuple the medical image as a simpleITK image and its dicom header.

    Elements
    --------
    simple_itk_image : Image
        Segmentation as a SimpleITK image.
    dicom_header : FileDataset
        Dicom header dataset.
    """
    simple_itk_image: sitk.Image
    dicom_header: pydicom.dataset.FileDataset = None


class PhysicalSpaceTransform(MapTransform):
    """
    PhysicalSpaceTransform abstract class.
    """

    def __init__(self, keys: KeysCollection) -> None:
        """
        Initialize transform keys.

        Parameters
        ----------
        keys : KeysCollection
            Keys of the corresponding items to be transformed. Image keys are assumed to be arbitrary series keys
            defined in 'tag_values'. For the label maps, the keys are organ names. Note that if
            'tag_values' is None, the image keys are assumed to be modality names.
        """
        super().__init__(keys=keys, allow_missing_keys=True)
        self._mode = Mode.NONE

    @property
    def mode(self) -> Mode:
        """
        The transform mode, i.e. whether the single ITK images on which to apply the transformation are images OR
        segmentations.

        Returns
        -------
        mode : Mode
            Transform mode.
        """
        return self._mode

    @mode.setter
    def mode(self, mode: Mode):
        """
        The transform mode, i.e. whether the single ITK images on which to apply the transformation are images OR
        segmentations.

        Parameters
        ----------
        mode : Mode
            The transform mode, i.e. whether the single ITK images on which to apply the transformation are images OR
            segmentations.
        """
        self._mode = mode

    @abstractmethod
    def __call__(self, data: Dict[str, ImageData]) -> Dict[Hashable, sitk.Image]:
        """
        Apply the transformation.

        Parameters
        ----------
        data : Dict[str, ImageData]
            A Python dictionary that contains ImageData.

        Returns
        -------
        transformed_data : Dict[Hashable, sitk.Image]
            A Python dictionary that contains transformed SimpleITK images.
        """
        raise NotImplementedError
