"""
    @file:              data_model.py
    @Author:            Maxence Larose

    @Creation Date:     10/2021
    @Last modification: 01/2022

    @Description:       This file contains several named tuples that are used to standardize the structure of objects
                        containing data.
"""

from dataclasses import dataclass
from typing import Dict, List, Sequence

import pydicom
import SimpleITK as sitk


@dataclass
class SegmentationDataModel:
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


@dataclass
class ImageDataModel:
    """
    A named tuple grouping the patient's dicom header, its medical image as a simpleITK image and a sequence of the
    paths to each dicom contained in the series.

    Elements
    --------
    dicom_header : FileDataset
        Dicom header dataset.
    simple_itk_image : Image
        Segmentation as a SimpleITK image.
    paths_to_dicoms : Sequence[str]
        A list of the paths to each dicom contained in the series.
    """
    dicom_header: pydicom.dataset.FileDataset
    simple_itk_image: sitk.Image
    paths_to_dicoms: Sequence[str]


@dataclass
class ImageAndSegmentationDataModel:
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


@dataclass
class PatientDataModel:
    """
    A named tuple grouping the patient's data extracted from its dicom files and the patient's medical image
    segmentation data extracted from the segmentation files, for each available modality. The patient data model is
    formatted as follows :

        PatientDataModel = (
            "patient_id": str,
            "data": [
                ImageAndSegmentationDataModel,
                ImageAndSegmentationDataModel
                ...
            ]
        )
    """
    patient_id: str
    data: List[ImageAndSegmentationDataModel]
