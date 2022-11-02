"""
    @file:              tools.py
    @Author:            Maxence Larose

    @Creation Date:     10/2022
    @Last modification: 10/2022

    @Description:       This file contains some tools to help applying transforms on images.
"""

from typing import Union

from monai.data import MetaTensor
from monai.utils import convert_to_numpy as monai_convert_to_numpy
import numpy as np

from dicom2hdf.data_model import PatientDataModel


def set_transforms_keys(patient_dataset: PatientDataModel) -> None:
    """
    Sets transforms keys.

    Parameters
    ----------
    patient_dataset : PatientDataModel
        Patient dataset.
    """
    keys = []
    for image_and_segmentation_data in patient_dataset.data:
        series_key = image_and_segmentation_data.image.series_key
        modality = image_and_segmentation_data.image.dicom_header.Modality

        if series_key and series_key in keys:
            raise AssertionError(f"Series key {series_key} already in dict. To use 'transforms', there must be only "
                                 f"one image associated to a given series key.")
        elif series_key:
            image_and_segmentation_data.image.transforms_key = series_key
            keys.append(series_key)
        elif modality in keys:
            raise AssertionError(f"Modality {modality} already in dict. To use 'transforms' without using "
                                 f"'series_descriptions', there must be only one image associated to a given modality. "
                                 f"Otherwise, use 'series_descriptions'.")
        else:
            image_and_segmentation_data.image.transforms_key = modality
            keys.append(modality)


def convert_to_numpy(array: Union[MetaTensor, np.ndarray]) -> np.ndarray:
    """
    Converts given image tensor or array to numpy array.

    Parameters
    ----------
    array : Union[MetaTensor, np.ndarray]
        Image tensor or array.

    Returns
    -------
    array : np.ndarray
        Image numpy array.
    """
    if isinstance(array, MetaTensor):
        return monai_convert_to_numpy(array[0, :])
    else:
        return array
