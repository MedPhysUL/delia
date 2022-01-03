"""
    @file:              request_context.py
    @Author:            Maxence Larose

    @Creation Date:     01/2022
    @Last modification: 01/2022

    @Description:       This file contains the class RequestContext that is used as a context class where strategies are
                        types of requests the client could ask the PatientDataReader class.
"""

from typing import Dict, List

from src.data_model import ImageDataModel, PatientDataModel
from src.constants.patient_data_strategy import PatientDataStrategy, PatientDataStrategies


class PatientDataContext:
    """
    A class used as a context class where strategies are types of requests the client could make to the
    PatientDataReader class to get the patient's data.
    """

    def __init__(
            self,
            images_data: List[ImageDataModel],
            paths_to_segmentations: List[str],
            series_descriptions: Dict[str, List[str]]
    ):
        """
        Constructor of the RequestContext class.

        Parameters
        ----------
        images_data : List[ImageDataModel]
            A list of the patient's images data.
        paths_to_segmentations : List[str]
            A list of paths to the segmentation files. The name of the segmentation files must include the series uid
            of their corresponding image, i.e. the image on which the segmentation was made.
        series_descriptions : Dict[str, List[str]]
            A dictionary that contains the series descriptions of the images that absolutely needs to be extracted from
            the patient's file. Keys are arbitrary names given to the images we want to add and values are lists of
            series descriptions. The images associated with these series descriptions do not need to have a
            corresponding segmentation. In fact, the whole point of adding a way to specify the series descriptions that
            must be added to the dataset is to be able to add images without segmentation.
        """
        self._images_data = images_data
        self._paths_to_segmentations = paths_to_segmentations
        self._series_descriptions = series_descriptions

    @property
    def patient_data_strategy(self) -> PatientDataStrategy:
        """
        Patient data request strategy corresponding to the given paths to segmentations and series descriptions
        configuration.

        Returns
        -------
        patient_data_strategy : PatientDataStrategy
            Patient data strategy.
        """
        if self._paths_to_segmentations and self._series_descriptions:
            return PatientDataStrategies.SEGMENTATION_AND_SERIES_DESCRIPTION
        elif self._paths_to_segmentations is None and self._series_descriptions:
            return PatientDataStrategies.SERIES_DESCRIPTION
        elif self._paths_to_segmentations and self._series_descriptions is None:
            return PatientDataStrategies.SEGMENTATION
        else:
            return PatientDataStrategies.DEFAULT

    @property
    def _factory_instance(self) -> PatientDataStrategy.factory:
        """
        The factory class instance corresponding to the class of the given patient data strategy.

        Returns
        -------
        _factory_instance : PatientDataStrategy.factory
            Factory class instance used to get a patient's data.
        """
        _factory_instance = self.patient_data_strategy.factory(
            images_data=self._images_data,
            paths_to_segmentations=self._paths_to_segmentations,
            series_descriptions=self._series_descriptions
        )

        return _factory_instance

    def create_patient_data(self) -> PatientDataModel:
        """
        Creates a tuple containing all the patient's data.

        Returns
        -------
        patient_data: PatientDataModel
            Patient data.
        """
        return self._factory_instance.create_patient_data()
