"""
    @file:              base_patient_data_factory.py
    @Author:            Maxence Larose

    @Creation Date:     01/2022
    @Last modification: 01/2022

    @Description:       This file contains the class BasePatientDataFactory that is used as an abstract class used as a
                        reference for all other patient data factories.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional

from src.data_model import ImageDataModel, PatientDataModel


class BasePatientDataFactory(ABC):
    """
    An abstract class that is used as a reference for all other patient data factories.
    """

    def __init__(
            self,
            images_data: List[ImageDataModel],
            organs: Dict[str, List[str]],
            paths_to_segmentations: Optional[List[str]] = None,
            series_descriptions: Optional[Dict[str, List[str]]] = None
    ):
        """
        Constructor of the class BasePatientDataFactory.

        Parameters
        ----------
        images_data : List[ImageDataModel]
            A list of the patient's images data.
        organs : Dict[str, List[str]]
            A dictionary that contains the organs and their associated segment names. Keys are arbitrary organ names
            and values are lists of possible segment names.
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
        self._images_data = images_data
        self._organs = organs
        self._paths_to_segmentations = paths_to_segmentations
        self._series_descriptions = series_descriptions

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

    @abstractmethod
    def create_patient_data(self) -> PatientDataModel:
        """
        Creates a tuple containing all the patient's data.

        Returns
        -------
        patient_data: PatientDataModel
            Patient data.
        """
        pass
