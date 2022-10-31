"""
    @file:              transforms.py
    @Author:            Maxence Larose

    @Creation Date:     10/2022
    @Last modification: 10/2022

    @Description:       This file contains the Dicom2hdfTransform abstract class which is used to define transforms
                        that can be applied to images and segmentations.
"""

from typing import Optional, Sequence, Union

from monai.transforms import apply_transform, Compose

from dicom2hdf.data_model import ImageDataModel, SegmentationDataModel
from dicom2hdf.transforms.transforms import Dicom2hdfTransform, Mode


def _set_mode(
        transforms: Union[Compose, Dicom2hdfTransform],
        mode: Mode
) -> None:
    """
    Set transforms mode.

    Parameters
    ----------
    transforms : Union[Compose, Dicom2hdfTransform]
        Transforms.
    mode : Mode
        Mode.
    """
    if isinstance(transforms, Compose):
        for t in transforms.transforms:
            t.mode = mode.value
    elif isinstance(transforms, Dicom2hdfTransform):
        transforms.mode = mode.value
    else:
        raise AssertionError("transforms must be either Compose or Dicom2hdfTransform")


def apply_transforms(
        transforms: Union[Compose, Dicom2hdfTransform],
        image: ImageDataModel,
        segmentations: Optional[Sequence[SegmentationDataModel]] = None
) -> None:
    """
    Apply transforms to image and segmentation.

    Parameters
    ----------
    transforms : Optional[Union[Compose, Dicom2hdfTransform]]
        A sequence of transformations to apply to images and segmentations in the physical space, i.e on the
        SimpleITK image. Keys are assumed to be modality names for images and organ names for segmentations.
    image : ImageDataModel
        The patient's medical image data.
    segmentations : Optional[Sequence[SegmentationDataModel]]
        Data from the segmentation of the patient's medical image.
    """
    image_modality = image.dicom_header.Modality
    temp_dict = {image_modality: image.simple_itk_image}
    _set_mode(transforms=transforms, mode=Mode.IMAGE)
    image.simple_itk_image = apply_transform(transform=transforms, data=temp_dict)[image_modality]

    if segmentations:
        _set_mode(transforms=transforms, mode=Mode.SEGMENTATION)
        for segmentation_data in segmentations:
            temp_dict = {}
            for organ_name, label_map in segmentation_data.simple_itk_label_maps.items():
                temp_dict[organ_name] = label_map

            segmentation_data.simple_itk_label_maps = apply_transform(transform=transforms, data=temp_dict)

    _set_mode(transforms=transforms, mode=Mode.NONE)
