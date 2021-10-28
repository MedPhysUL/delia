from typing import Dict, List, NamedTuple

import pydicom
import SimpleITK as sitk
import numpy as np


class SegmentDataModel(NamedTuple):
    """
    A named tuple grouping all the important information of a specific segment in the segmentation.

    Elements
    --------
    name : str
        The segment name.
    layer : int
        The layer of the segment in the 4D mask array.
    label_value : int
        The label value of the segment in the 3D mask array.
    """
    name: str = None
    layer: int = None
    label_value: int = None


class SegmentationDataModel(NamedTuple):
    """
    A named tuple grouping the segmentation as several binary label maps (one for each organ in the segmentation), the
    segmentation as a simpleITK image, and finally, metadata about the organs/segments that are found in the
    segmentation.

    Elements
    --------
    binary_label_maps : Dict[str, np.ndarray]
        Dictionary grouping organs to their corresponding binary label map. The keys are organ names and the values are
        the binary label maps. The binary label maps dictionary is formatted as follows :

            binary_label_maps = {
                organ_name (example: "PROSTATE"): np.ndarray,
                organ_name (example: "RECTUM"): np.ndarray,
                ...
            }

    simple_itk_label_map : Image
        The segmentation has a SimpleITK image.
    metadata : Dict[str, SegmentDataModel]
        A dictionary that contains organs and their corresponding segmentation metadata. Keys are organ names and
        values are tuples containing important information about the segments in the original segmentation image
        (segments name, segments layer, segments label value, etc.). Thus, the segmentation metadata dictionary is
        formatted as follows :

            metadata = {
                organ_name (example: "PROSTATE"): (
                    name: str
                    layer: int
                    label_value: int
                ),
                organ_name (example: "RECTUM"): (
                    name: str
                    layer: int
                    label_value: int
                ),
                ...
            }
    """
    binary_label_maps: Dict[str, np.ndarray] = None
    simple_itk_label_map: sitk.Image = None
    metadata: Dict[str, SegmentDataModel] = None


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
