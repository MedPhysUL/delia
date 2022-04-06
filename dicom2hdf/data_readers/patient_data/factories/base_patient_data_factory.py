"""
    @file:              base_patient_data_factory.py
    @Author:            Maxence Larose

    @Creation Date:     01/2022
    @Last modification: 03/2022

    @Description:       This file contains the class BasePatientDataFactory that is used as an abstract class used as a
                        reference for all other patient data factories.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional

from dicom2hdf.data_model import PatientDataModel
from dicom2hdf.data_readers.image.dicom_reader import DicomReader


class BasePatientDataFactory(ABC):
    """
    An abstract class that is used as a reference for all other patient data factories.
    """

    def __init__(
            self,
            path_to_patient_folder: str,
            paths_to_segmentations: Optional[List[str]],
            series_descriptions: Optional[Dict[str, List[str]]]
    ):
        """
        Constructor of the class BasePatientDataFactory.

        Parameters
        ----------
        path_to_patient_folder : str
            Path to the folder containing the patient's image files.
        paths_to_segmentations : Optional[List[str]]
            List of paths to the patient's segmentation files.
        series_descriptions : Optional[Dict[str, List[str]]]
            A dictionary that contains the series descriptions of the images that absolutely needs to be extracted from
            the patient's file. Keys are arbitrary names given to the images we want to add and values are lists of
            series descriptions.
        """
        self._path_to_patient_folder = path_to_patient_folder
        self._paths_to_segmentations = paths_to_segmentations
        self._series_descriptions = series_descriptions

        dicom_reader = DicomReader(path_to_patient_folder=self._path_to_patient_folder)
        self._images_data = dicom_reader.get_images_data(remove_segmentations=True)

    @property
    def patient_id(self) -> str:
        """
        Patient ID.

        Returns
        -------
        patient_id : str
            Patient ID.
        """
        patient_id = self._images_data[0].dicom_header.PatientID

        return str(patient_id)

    @abstractmethod
    def create_patient_data(self) -> PatientDataModel:
        """
        Creates a tuple containing all the patient's data.

        Returns
        -------
        patient_data: PatientDataModel
            Patient data.
        """
        raise NotImplementedError
