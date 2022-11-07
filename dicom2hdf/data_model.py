"""
    @file:              data_model.py
    @Author:            Maxence Larose

    @Creation Date:     10/2021
    @Last modification: 10/2022

    @Description:       This file contains several named tuples that are used to standardize the structure of objects
                        containing data.
"""

from dataclasses import dataclass
from typing import Dict, Optional, List, Sequence

import numpy as np
import pydicom
import SimpleITK as sitk

from dicom2hdf.transforms_history import TransformsHistory


@dataclass
class SegmentationDataModel:
    """
    A named tuple grouping the segmentation as several binary label maps (one for each organ in the segmentation) and
    the segmentation as a simpleITK image.

    Elements
    --------
    modality : str
        Segmentation modality (ex: SEG, RTSTRUCT).
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
    modality: Optional[str] = None
    simple_itk_label_maps: Optional[Dict[str, sitk.Image]] = None

    @property
    def numpy_array_label_maps(self) -> Optional[Dict[str, np.ndarray]]:
        if self.simple_itk_label_maps:
            return {k: sitk.GetArrayFromImage(v) for k, v in self.simple_itk_label_maps.items()}
        else:
            return None


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
        Dicom data volume as a SimpleITK image.
    paths_to_dicoms : Sequence[str]
        A list of the paths to each dicom contained in the series.
    series_key : str
        Arbitrary name given to the image we want to extract.
    _transforms_key : str
        key used for the temporary dictionary created when applying transforms.
    """
    dicom_header: pydicom.dataset.FileDataset
    paths_to_dicoms: Sequence[str]
    simple_itk_image: sitk.Image
    series_key: Optional[str] = None
    transforms_key: Optional[str] = None
        
    @property
    def numpy_array(self) -> np.ndarray:
        return sitk.GetArrayFromImage(self.simple_itk_image)


@dataclass
class ImageAndSegmentationDataModel:
    """
    A named tuple grouping the patient data retrieved from his dicom files and the segmentation data retrieved from
    the segmentation file.

    Elements
    --------
    image : ImageDataModel
        The patient's medical image data.
    segmentation : Sequence[SegmentationDataModel]
        Data from the segmentation of the patient's medical image.
    """
    image: ImageDataModel
    segmentations: Optional[Sequence[SegmentationDataModel]] = None


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
            "transforms_history" : TransformsHistory
        )
    """
    patient_id: str
    data: List[ImageAndSegmentationDataModel]
    transforms_history: Optional[TransformsHistory] = None
