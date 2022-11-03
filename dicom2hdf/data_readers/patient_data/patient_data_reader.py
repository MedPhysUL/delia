"""
    @file:              patient_data_reader.py
    @Author:            Maxence Larose

    @Creation Date:     10/2021
    @Last modification: 10/2022

    @Description:       This file contains the PatientDataReader class which is used to read dicom files AND
                        segmentation files.
"""

import logging
from typing import Dict, List, Optional, Union

from monai.transforms import Compose
from monai.transforms import MapTransform as MonaiMapTransform

from dicom2hdf.data_model import PatientDataModel
from dicom2hdf.data_readers.image.dicom_reader import DicomReader
from dicom2hdf.data_readers.patient_data.patient_data_query_context import PatientDataQueryContext
from dicom2hdf.transforms.applications import apply_transforms
from dicom2hdf.transforms.history import TransformsHistory
from dicom2hdf.transforms.transforms import Dicom2hdfTransform

_logger = logging.getLogger(__name__)


class PatientDataReader(DicomReader):
    """
    A class used to read dicom files AND segmentation files.
    """

    def __init__(
            self,
            path_to_patient_folder: str,
            series_descriptions: Optional[Dict[str, List[str]]],
            erase_unused_dicom_files: bool = False
    ):
        """
        Used to check availability of given series' uid and series descriptions in the patient's dicom files.

        Parameters
        ----------
        path_to_patient_folder : str
            Path to the folder containing the patient's files.
        series_descriptions : Dict[str, List[str]]
            A dictionary that contains the series descriptions of the images that absolutely needs to be extracted from
            the patient's file. Keys are arbitrary names given to the images we want to add and values are lists of
            series descriptions.
        erase_unused_dicom_files: bool = False
            Whether to delete unused DICOM files or not. Use with caution.
        """
        super().__init__(path_to_patient_folder=path_to_patient_folder)

        self._images_dicom_headers = self.get_dicom_headers(remove_segmentations=True)
        self._series_descriptions = series_descriptions
        self._erase_unused_dicom_files = erase_unused_dicom_files

        self.failed_images = []
        if series_descriptions is not None:
            self.check_availability_of_given_series_description()

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
    def series_descriptions(self) -> Dict[str, List[str]]:
        """
        Series descriptions setter.

        Returns
        -------
        series_descriptions : Dict[str, List[str]]
            A dictionary that contains the series descriptions of the images that absolutely needs to be extracted from
            the patient's file. Keys are arbitrary names given to the images we want to add and values are lists of
            series descriptions.
        """
        return self._series_descriptions

    @series_descriptions.setter
    def series_descriptions(self, series_descriptions: Dict[str, List[str]]):
        """
        Series descriptions setter.

        Parameters
        ----------
        series_descriptions : Dict[str, List[str]]
            A dictionary that contains the series descriptions of the images that absolutely needs to be extracted from
            the patient's file. Keys are arbitrary names given to the images we want to add and values are lists of
            series descriptions.
        """
        items = list(series_descriptions.items())
        for previous_items, current_items in zip(items, items[1:]):
            set_intersection = set(previous_items[1]) & set(current_items[1])

            if bool(set_intersection):
                raise AssertionError(f"\nThe dictionary of series descriptions should not contain the same series names"
                                     f" for different images/modalities. \nHowever, here we find the series names "
                                     f"{previous_items[1]} for the {previous_items[0]} image and {current_items[1]} "
                                     f"for the {current_items[0]} image. \nClearly, the images series values are "
                                     f"overlapping because of the series named {set_intersection}.")

        self.series_descriptions = series_descriptions

    @property
    def available_series_descriptions(self) -> List[str]:
        """
        Available series descriptions.

        Returns
        -------
        available_series_descriptions : List[str]
            Available series descriptions in the patient dicom files.
        """
        available_series_descriptions = [
            self._get_series_description(dicom_header) for dicom_header in self._images_dicom_headers
        ]

        return available_series_descriptions

    def check_availability_of_given_series_description(self) -> None:
        """
        Check availability of given series description in the patient's dicom files.
        """
        _logger.debug("Checking availability of given series description...")
        for series_key, series_description_list in self.series_descriptions.items():
            if any(series in self.available_series_descriptions for series in series_description_list):
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
        _logger.error(f"Patient with ID {self.patient_id} has no series available that correlates with the "
                      f"image '{series_key}'. The expected series descriptions for this image are "
                      f"{self.series_descriptions[series_key]} while the patient record only contains the following "
                      f"series descriptions: {self.available_series_descriptions}.")

        self.failed_images.append(series_key)

    def get_patient_dataset(
            self,
            transforms: Optional[Union[Compose, Dicom2hdfTransform, MonaiMapTransform]] = None
    ) -> PatientDataModel:
        """
        Get the patient dataset.

        Parameters
        ----------
        transforms : Optional[Union[Compose, Dicom2hdfTransform, MonaiMapTransform]]
            A sequence of transformations to apply to images and segmentations. Dicom2hdfTransform are applied in the
            physical space, i.e on the SimpleITK image, while MonaiMapTransform are applied in the array space, i.e on
            the numpy array that represents the image. The keys for images are assumed to be the arbitrary series key
            set in 'series_descriptions'. For segmentation, keys are organ names. Note that if 'series_descriptions' is
            None, the keys for images are assumed to be modalities.

        Returns
        -------
        patient_dataset : PatientDataModel
            A named tuple grouping the patient's data extracted from its DICOM files and the patient's medical image
            segmentation data extracted from the segmentation files.
        """
        patient_data_context = PatientDataQueryContext(
            path_to_patient_folder=self._path_to_patient_folder,
            paths_to_segmentations=self.paths_to_segmentations,
            series_descriptions=self._series_descriptions,
            erase_unused_dicom_files=self._erase_unused_dicom_files
        )
        patient_dataset = patient_data_context.create_patient_data()

        if transforms:
            apply_transforms(patient_dataset=patient_dataset, transforms=transforms)

        _logger.debug(f"Chosen patient data query strategy : "
                      f"'{patient_data_context.patient_data_query_strategy.name}'.")
        _logger.info(f"{len(patient_dataset.data)} images added to the patient dataset, namely: ")

        for image_and_segmentation_data in patient_dataset.data:
            image = image_and_segmentation_data.image
            segmentations = image_and_segmentation_data.segmentations

            modality = image.dicom_header.Modality
            series_description = image.dicom_header.SeriesDescription
            image_segmentation_available = True if segmentations else False

            segmented_organs = set()
            if segmentations:
                for segmentation in segmentations:
                    for organ in list(segmentation.simple_itk_label_maps.keys()):
                        segmented_organs.add(organ)

            _logger.info(f"Series Description : {series_description}")
            _logger.info(f"  Modality : {modality}")
            _logger.info(f"  Image Segmentation available: {image_segmentation_available}")

            if image_segmentation_available:
                _logger.info(f"  Segmented organs : {segmented_organs}")

        patient_dataset.transforms_history = TransformsHistory(transforms)

        return patient_dataset
