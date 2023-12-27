"""
    @file:              patient_data_reader.py
    @Author:            Maxence Larose

    @Creation Date:     10/2021
    @Last modification: 10/2022

    @Description:       This file contains the PatientDataReader class which is used to read dicom files AND
                        segmentation files.
"""

import logging
from typing import Dict, List, Optional, Tuple, Union

from monai.transforms import Compose
from monai.transforms import MapTransform as MonaiMapTransform

from delia.readers.image.dicom_reader import DicomReader
from delia.readers.patient_data.patient_data_query_context import PatientDataQueryContext
from delia.transforms.applications import apply_transforms
from delia.transforms.data.transform import DataTransform
from delia.transforms.physical_space.transform import PhysicalSpaceTransform
from delia.utils.data_model import PatientDataModel
from delia.utils.transforms_history import TransformsHistory

_logger = logging.getLogger(__name__)


class PatientDataReader(DicomReader):
    """
    A class used to read dicom files AND segmentation files.
    """

    def __init__(
            self,
            path_to_patient_folder: str,
            tag_values: Optional[Dict[str, List[str]]],
            tag: Union[str, Tuple[int, int]],
            load_segmentations: bool = True,
            organs: Optional[List[str]] = None,
            erase_unused_dicom_files: bool = False
    ):
        """
        Used to check availability of given series' uid and tag values in the patient's dicom files.

        Parameters
        ----------
        path_to_patient_folder : str
            Path to the folder containing the patient's files.
        tag_values : Dict[str, List[str]]
            A dictionary that contains the desired tag's values for the images that absolutely needs to be extracted
            from the patient's file. Keys are arbitrary names given to the images we want to add and values are lists of
            values associated with the specified tag.
        tag : Union[str, Tuple[int, int]]
            Keyword or tuple of the DICOM tag to use while selecting which files to extract.
        load_segmentations : bool = True
            Whether to load the segmentation files or not.
        organs : Optional[List[str]] = None
            List of organs to load. If None, all organs will be loaded.
        erase_unused_dicom_files: bool = False
            Whether to delete unused DICOM files or not. Use with caution.
        """
        super().__init__(
            path_to_patient_folder=path_to_patient_folder,
            tag=tag,
            load_segmentations=load_segmentations
        )

        self._images_dicom_headers = self.get_dicom_headers(remove_segmentations=True)
        self._tag_values = tag_values
        self._erase_unused_dicom_files = erase_unused_dicom_files
        self._organs = organs
        self._path_to_patient_folder = path_to_patient_folder

        self.failed_images = []
        if tag_values is not None:
            self.check_availability_of_given_tag_value()

    @property
    def patient_id(self) -> str:
        """
        Patient ID.

        Returns
        -------
        patient_id : str
            Patient id.
        """
        return str(self._images_dicom_headers[0].PatientID)

    @property
    def patient_path(self) -> str:
        """
        Patient Path.

        Returns
        -------
        patient_path : str
            Patient folder path
        """
        return str(self._path_to_patient_folder)

    @property
    def paths_to_segmentations(self) -> List[str]:
        """
        Paths to segmentations.

        Returns
        -------
        paths_to_segmentations : List[str]
            List of paths to the segmentation files.
        """
        paths_to_segmentations = [
            series.paths_to_dicoms_from_series[0] for series in self._segmentations_series_data_dict.values()
        ]

        return paths_to_segmentations

    @property
    def tag_values(self) -> Dict[str, List[str]]:
        """
        Tag values setter.

        Returns
        -------
        tag_values : Dict[str, List[str]]
            A dictionary that contains the desired tag's values for the images that absolutely needs to be extracted
            from the patient's file. Keys are arbitrary names given to the images we want to add and values are lists of
            values associated with the specified tag.
        """
        return self._tag_values

    @tag_values.setter
    def tag_values(self, tag_values: Dict[str, List[str]]):
        """
        Tag values setter.

        Parameters
        ----------
        tag_values : Dict[str, List[str]]
            A dictionary that contains the desired tag's values for the images that absolutely needs to be extracted
            from the patient's file. Keys are arbitrary names given to the images we want to add and values are lists of
            values associated with the specified tag.
        """
        items = list(tag_values.items())
        for previous_items, current_items in zip(items, items[1:]):
            set_intersection = set(previous_items[1]) & set(current_items[1])

            if bool(set_intersection):
                raise AssertionError(
                    f"\nThe dictionary of tag values should not contain the same series names for different "
                    f"images/modalities. \nHowever, here we find the series names {previous_items[1]} for the "
                    f"{previous_items[0]} image and {current_items[1]} for the {current_items[0]} image. \nClearly, "
                    f"the images series values are overlapping because of the series named {set_intersection}."
                )

        self.tag_values = tag_values

    @property
    def available_tag_values(self) -> List[str]:
        """
        Available values of the specified tag.

        Returns
        -------
        available_tag_values : List[str]
            Available values of the specified tag in the patient dicom files.
        """
        available_tag_values = [
            self._get_tag_value(dicom_header, self.tag) for dicom_header in self._images_dicom_headers
        ]

        return available_tag_values

    def check_availability_of_given_tag_value(self) -> None:
        """
        Check availability of given value for specified tag in the patient's dicom files.
        """
        _logger.debug("Checking availability of given value for specified tag...")
        for series_key, tag_value_list in self.tag_values.items():
            if any(series in self.available_tag_values for series in tag_value_list):
                pass
            else:
                self.record_failed_images(series_key)
        _logger.debug("Done.")

    def record_failed_images(self, series_key: str) -> None:
        """
        Record failed images.

        Parameters
        ----------
        series_key : str
            Series key.
        """
        _logger.error(
            f"Patient with ID {self.patient_id} has no series available that correlates with the image '{series_key}'. "
            f"The expected values of specified tag for this image are {self.tag_values[series_key]} while the "
            f"patient record only contains the following values: {self.available_tag_values}."
        )

        self.failed_images.append(series_key)

    def get_patient_dataset(
            self,
            transforms: Optional[Union[Compose, DataTransform, MonaiMapTransform, PhysicalSpaceTransform]] = None
    ) -> PatientDataModel:
        """
        Get the patient dataset.

        Parameters
        ----------
        transforms : Union[Compose, DataTransform, MonaiMapTransform, PhysicalSpaceTransform]
            A sequence of transformations to apply. PhysicalSpaceTransform are applied in the physical space, i.e on
            the SimpleITK image, while MonaiMapTransform are applied in the array space, i.e on the numpy array that
            represents the image. DataTransform transforms the data using other a patient's other images or
            segmentations. The keys for images are assumed to be the arbitrary series key set in 'tag_values'.
            For segmentation, keys are organ names. Note that if 'tag_values' is None, the keys for images are
            assumed to be modalities.

        Returns
        -------
        patient_dataset : PatientDataModel
            A named tuple grouping the patient's data extracted from its DICOM files and the patient's medical image
            segmentation data extracted from the segmentation files.
        """
        patient_data_context = PatientDataQueryContext(
            path_to_patient_folder=self._path_to_patient_folder,
            paths_to_segmentations=self.paths_to_segmentations,
            tag_values=self._tag_values,
            tag=self.tag,
            organs=self._organs,
            erase_unused_dicom_files=self._erase_unused_dicom_files
        )
        patient_dataset = patient_data_context.create_patient_data()

        if transforms:
            apply_transforms(patient_dataset=patient_dataset, transforms=transforms)

        _logger.debug(
            f"Chosen patient data query strategy: '{patient_data_context.patient_data_query_strategy.name}'."
        )
        _logger.info(f"{len(patient_dataset.data)} images added to the patient dataset, namely: ")

        for image_and_segmentation_data in patient_dataset.data:
            image = image_and_segmentation_data.image
            segmentations = image_and_segmentation_data.segmentations

            segmented_organs = set()
            if segmentations:
                for segmentation in segmentations:
                    for organ in list(segmentation.simple_itk_label_maps.keys()):
                        segmented_organs.add(organ)

            if hasattr(image.dicom_header, "SeriesDescription"):
                series_description = image.dicom_header.SeriesDescription
                _logger.info(f"Series Description : {series_description}")

            if hasattr(image.dicom_header, "Modality"):
                modality = image.dicom_header.Modality
                _logger.info(f"  Modality : {modality}")

            image_segmentation_available = True if segmentations else False
            _logger.info(f"  Image Segmentation available: {image_segmentation_available}")

            if image_segmentation_available:
                _logger.info(f"  Segmented organs : {segmented_organs}")

        patient_dataset.transforms_history = TransformsHistory(transforms)

        return patient_dataset
