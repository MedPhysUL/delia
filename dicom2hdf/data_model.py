"""
    @file:              data_model.py
    @Author:            Maxence Larose

    @Creation Date:     10/2021
    @Last modification: 01/2022

    @Description:       This file contains several named tuples that are used to standardize the structure of objects
                        containing data.
"""

from typing import Dict, List, NamedTuple

import pydicom
import SimpleITK as sitk


class SegmentationDataModel(NamedTuple):
    """
    A named tuple grouping the segmentation as several binary label maps (one for each organ in the segmentation) and
    the segmentation as a simpleITK image.

    Elements
    --------
    simple_itk_label_maps : Dict[str, sitk.Image]
        A dictionary that contains the name of the organs and their corresponding binary label map as a simpleITK
        image. Keys are organ names and values are binary label maps. Thus, the label maps dictionary is formatted
        as follows :

            label_maps = {
                organ_name (example: "PROSTATE"): sitk.Image,
                organ_name (example: "RECTUM"): sitk.Image,
                ...
            }
    """
    simple_itk_label_maps: Dict[str, sitk.Image] = None


class ImageDataModel(NamedTuple):
    """
    A named tuple grouping the patient's dicom header and its medical image as a simpleITK image.

    Elements
    --------
    dicom_header : FileDataset
        Dicom header dataset.
    simple_itk_image : Image
        Segmentation as a SimpleITK image.
    """
    dicom_header: pydicom.dataset.FileDataset
    simple_itk_image: sitk.Image


class ImageAndSegmentationDataModel(NamedTuple):
    """
    A named tuple grouping the patient data retrieved from his dicom files and the segmentation data retrieved from
    the segmentation file.

    Elements
    --------
    image : ImageDataModel
        The patient's medical image data.
    segmentation : SegmentationDataModel
        Data from the segmentation of the patient's medical image.
    """
    image: ImageDataModel
    segmentation: SegmentationDataModel = None


class PatientDataModel(NamedTuple):
    """
    A named tuple grouping the patient's data extracted from its dicom files and the patient's medical image
    segmentation data extracted from the segmentation files, for each available modality. The patient data model is
    formatted as follows :

        PatientDataModel = (
            "patient_name": str,
            "data": [
                ImageAndSegmentationDataModel,
                ImageAndSegmentationDataModel
                ...
            ]
        )
    """
    patient_name: str
    data: List[ImageAndSegmentationDataModel]
