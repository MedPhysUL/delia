"""
    @file:              patient_data_reader.py
    @Author:            Maxence Larose

    @Creation Date:     10/2021
    @Last modification: 01/2022

    @Description:       This file contains the PatientDataReader class which is used to read dicom files AND
                        segmentation files.
"""

import enum
import logging
from typing import Callable, Dict, List, NamedTuple, Optional

from src.data_model import ImageAndSegmentationDataModel, PatientDataModel
from .dicom_reader import DicomReader
from src.data_readers.patient_data.patient_data_context import PatientDataContext
from .segmentation_reader import SegmentationReader


class PatientDataReader(DicomReader):
    """
    A class used to read dicom files AND segmentation files.
    """

    def __init__(
            self,
            path_to_dicom_folder: str,
            paths_to_segmentations: Optional[List[str]] = None,
            series_descriptions: Optional[Dict[str, List[str]]] = None
    ):
        """
        Used to check availability of given series' uid and series descriptions in the patient's dicom files.

        Parameters
        ----------
        path_to_dicom_folder : str
            Path to the folder containing the patient dicom files.
        paths_to_segmentations : Optional[List[str]]
            A list of paths to the segmentation files. The name of the segmentation files must include the series uid
            of their corresponding image, i.e. the image on which the segmentation was made.
        series_descriptions : Optional[Dict[str, List[str]]]
            A dictionary that contains the series descriptions of the images that absolutely needs to be extracted from
            the patient's file. Keys are arbitrary names given to the images we want to add and values are lists of
            series descriptions. The images associated with these series descriptions do not need to have a
            corresponding segmentation. In fact, the whole point of adding a way to specify the series descriptions that
            must be added to the dataset is to be able to add images without segmentation.
        """
        super(PatientDataReader, self).__init__(path_to_dicom_folder=path_to_dicom_folder)
        self._images_data = self.get_images_data()
        self._paths_to_segmentations = paths_to_segmentations
        self._series_descriptions = series_descriptions

        # self.check_availability_of_given_series_uids()
        # self.check_availability_of_given_series_description()

    @property
    def patient_name(self) -> str:
        """
        Patient name.

        Returns
        -------
        patient_name : str
            Patient name.
        """
        patient_name = self._images_data[0].dicom_header.PatientName

        return str(patient_name)

    @property
    def paths_to_segmentations(self) -> List[str]:
        """
        Paths to segmentations property.

        Returns
        -------
        paths_to_segmentations : List[str]
            A list of paths to the segmentation files. The name of the segmentation files must include the series uid
            of their corresponding image, i.e. the image on which the segmentation was made.
        """
        return self._paths_to_segmentations

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
        self._series_descriptions = series_descriptions

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
            image.dicom_header.SeriesDescription for image in self._images_data
        ]

        return available_series_descriptions

    @property
    def available_series_uids(self) -> List[str]:
        """
        Available series' uids.

        Returns
        -------
        available_series_uids : List[str]
            Available series uids in the patient dicom files.
        """
        available_series_uid = [
            image.dicom_header.SeriesInstanceUID for image in self._images_data
        ]

        return available_series_uid

    def update_series_descriptions(self, series_key: str) -> None:
        """
        Add a series description to the series description list of the given series key.

        Parameters
        ----------
        series_key : str
            Series key.
        """
        logging.info(f"No available series for {series_key}. Available series are "
                     f"{self.available_series_descriptions}.")

        while True:
            new_series_description = input("Name of the series description to add: ")

            if new_series_description in self.available_series_descriptions:
                break
            else:
                logging.info(f"The given series description name is {new_series_description}. However, this is NOT one "
                             f"of the available series description found in the patient's dicom files. Available "
                             f"series are {self.available_series_descriptions}. Please try again.")

        self.series_descriptions[series_key] += [new_series_description]

    def check_availability_of_given_series_description(self) -> None:
        """
        Check availability of given series description in the patient's dicom files.
        """
        for series_key, series_description_list in self.series_descriptions.items():
            if any(series in self.available_series_descriptions for series in series_description_list):
                pass
            else:
                self.update_series_descriptions(series_key)
                self.check_availability_of_given_series_description()

    def check_availability_of_given_series_uids(self) -> None:
        """
        Check availability of given series uids in the patient's dicom files.
        """
        for path_to_segmentation in self.paths_to_segmentations:
            if any(uid in path_to_segmentation for uid in self.available_series_uids):
                pass
            else:
                logging.warning(f"The given segmentation file name is {path_to_segmentation}. However, this file name "
                                f"does NOT contain any of the available series uids found in the patient's dicom "
                                f"files. Available series uids are {self.available_series_uids}.")

    def get_patient_dataset(self) -> PatientDataModel:
        """
        Get the patient dataset.

        Returns
        -------
        patient_dataset : PatientDataModel
            A named tuple grouping the patient's data extracted from its dicom files and the patient's medical image
            segmentation data extracted from the segmentation files.
        """
        patient_data_context = PatientDataContext(
            images_data=self._images_data,
            paths_to_segmentations=self._paths_to_segmentations,
            series_descriptions=self._series_descriptions
        )

        return patient_data_context.create_patient_data()
