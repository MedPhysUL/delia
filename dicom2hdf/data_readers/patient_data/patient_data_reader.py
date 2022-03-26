"""
    @file:              patient_data_reader.py
    @Author:            Maxence Larose

    @Creation Date:     10/2021
    @Last modification: 03/2022

    @Description:       This file contains the PatientDataReader class which is used to read dicom files AND
                        segmentation files.
"""

import logging
from typing import Dict, List, Optional

from dicom2hdf.data_model import PatientDataModel
from dicom2hdf.data_readers.image.dicom_reader import DicomReader
from dicom2hdf.data_readers.patient_data.patient_data_query_context import PatientDataQueryContext

_logger = logging.getLogger(__name__)


class PatientDataReader(DicomReader):
    """
    A class used to read dicom files AND segmentation files.
    """

    def __init__(
            self,
            path_to_images_folder: str,
            path_to_segmentations_folder: Optional[str],
            series_descriptions: Optional[Dict[str, List[str]]]
    ):
        """
        Used to check availability of given series' uid and series descriptions in the patient's dicom files.

        Parameters
        ----------
        path_to_images_folder : str
            Path to the folder containing the patient's image files.
        path_to_segmentations_folder : Optional[str]
            Path to the folder containing the patient's segmentation files.
        series_descriptions : Optional[Dict[str, List[str]]]
            A dictionary that contains the series descriptions of the images that absolutely needs to be extracted from
            the patient's file. Keys are arbitrary names given to the images we want to add and values are lists of
            series descriptions. The images associated with these series descriptions do not need to have a
            corresponding segmentation. In fact, the whole point of adding a way to specify the series descriptions that
            must be added to the dataset is to be able to add images without segmentation.
        """
        super(PatientDataReader, self).__init__(path_to_images_folder=path_to_images_folder)

        self._dicom_headers = self.get_dicom_headers()
        self._path_to_segmentations_folder = path_to_segmentations_folder
        self._series_descriptions = series_descriptions

        if series_descriptions is not None:
            self.check_availability_of_given_series_description()

    @property
    def patient_name(self) -> str:
        """
        Patient name.

        Returns
        -------
        patient_name : str
            Patient name.
        """
        return str(self._dicom_headers[0].PatientName)

    @property
    def path_to_segmentations_folder(self) -> str:
        """
        Paths to segmentations property.

        Returns
        -------
        path_to_segmentations_folder : List[str]
            Path to the folder containing the patient's segmentation files.
        """
        return self._path_to_segmentations_folder

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
            series descriptions. The images associated with these series descriptions do not need to have a
            corresponding segmentation. In fact, the whole point of adding a way to specify the series descriptions that
            must be added to the dataset is to be able to add images without segmentation. the patient dataset.
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
            dicom_header.SeriesDescription for dicom_header in self._dicom_headers
        ]

        return available_series_descriptions + ["None"]

    def update_series_descriptions(self, series_key: str) -> None:
        """
        Add a series description to the series description list of the given series key.

        Parameters
        ----------
        series_key : str
            Series key.
        """
        while True:
            new_series_description = input(
                f"\nNo available series for {series_key}. \nAvailable series are {self.available_series_descriptions}. "
                f"\nPlease write in the following location the name of the series to add. If the image does not require "
                f"any description, write None. \nName of the series description to add (modality = {series_key}): ")

            if new_series_description in self.available_series_descriptions:
                _logger.info("Series name successfully added to the series descriptions json file.\n")
                break
            else:
                _logger.info(f"The given series description name is {new_series_description}. \nHowever, this is NOT "
                             f"one of the available series description found in the patient's dicom files. \nAvailable "
                             f"series are {self.available_series_descriptions}. \nPlease try again.")

        self.series_descriptions[series_key] += [new_series_description]

    def check_availability_of_given_series_description(self) -> None:
        """
        Check availability of given series description in the patient's dicom files.
        """
        _logger.info("Checking availability of given series description...")
        for series_key, series_description_list in self.series_descriptions.items():
            if any(series in self.available_series_descriptions for series in series_description_list):
                pass
            else:
                self.update_series_descriptions(series_key)
                self.check_availability_of_given_series_description()
        _logger.info("Done.")

    def get_patient_dataset(self) -> PatientDataModel:
        """
        Get the patient dataset.

        Returns
        -------
        patient_dataset : PatientDataModel
            A named tuple grouping the patient's data extracted from its DICOM files and the patient's medical image
            segmentation data extracted from the segmentation files.
        """
        patient_data_context = PatientDataQueryContext(
            path_to_images_folder=self._path_to_images_folder,
            path_to_segmentations_folder=self._path_to_segmentations_folder,
            series_descriptions=self._series_descriptions
        )
        patient_dataset = patient_data_context.create_patient_data()

        _logger.debug(f"\nThe chosen patient data query strategy is called "
                      f"'{patient_data_context.patient_data_query_strategy.name}'.")
        _logger.info(f"\nA total of {len(patient_dataset.data)} images were added to the patient dataset, namely:")

        for image_and_segmentation_data in patient_dataset.data:
            modality = image_and_segmentation_data.image.dicom_header.Modality
            series_description = image_and_segmentation_data.image.dicom_header.SeriesDescription
            segmentation = image_and_segmentation_data.segmentation
            image_segmentation_available = True if segmentation else False
            segmented_organs = list(segmentation.simple_itk_label_maps.keys()) if segmentation else None

            _logger.info(f"---> Series Description ({series_description})"
                         f"\n     ---> Modality : {modality}"
                         f"\n     ---> Image Segmentation available: {image_segmentation_available}")

            if image_segmentation_available:
                _logger.info(f"     ---> Segmented organs : {segmented_organs}")

        return patient_dataset
