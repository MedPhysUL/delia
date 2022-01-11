"""
    @file:              patient_data_query_context.py
    @Author:            Maxence Larose

    @Creation Date:     01/2022
    @Last modification: 01/2022

    @Description:       This file contains the class PatientDataQueryContext that is used as a context class where strategies are
                        types of requests the client could ask the PatientDataReader class.
"""

from typing import Dict, List

from ...data_model import ImageDataModel, PatientDataModel
from .patient_data_query_strategy import PatientDataQueryStrategy, PatientDataQueryStrategies


class PatientDataQueryContext:
    """
    A class used as a context class where strategies are types of requests the client could make to the
    PatientDataReader class to get the patient's data.
    """

    def __init__(
            self,
            images_data: List[ImageDataModel],
            organs: Dict[str, List[str]],
            paths_to_segmentations: List[str],
            series_descriptions: Dict[str, List[str]]
    ):
        """
        Constructor of the PatientDataQueryContext class.

        Parameters
        ----------
        images_data : List[ImageDataModel]
            A list of the patient's images data.
        organs : Dict[str, List[str]]
            A dictionary that contains the organs and their associated segment names. Keys are arbitrary organ names
            and values are lists of possible segment names.
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
        self._organs = organs
        self._paths_to_segmentations = paths_to_segmentations
        self._series_descriptions = series_descriptions

    @property
    def patient_data_query_strategy(self) -> PatientDataQueryStrategy:
        """
        Patient data query strategy corresponding to the given paths to segmentations and series descriptions
        configuration.

        Returns
        -------
        patient_data_query_strategy : PatientDataQueryStrategy
            Patient data query strategy.
        """
        if self._paths_to_segmentations and self._series_descriptions:
            return PatientDataQueryStrategies.SEGMENTATION_AND_SERIES_DESCRIPTION
        elif self._paths_to_segmentations is None and self._series_descriptions:
            return PatientDataQueryStrategies.SERIES_DESCRIPTION
        elif self._paths_to_segmentations and self._series_descriptions is None:
            return PatientDataQueryStrategies.SEGMENTATION
        else:
            return PatientDataQueryStrategies.DEFAULT

    @property
    def _patient_data_factory_instance(self) -> PatientDataQueryStrategy.factory:
        """
        The factory class instance corresponding to the class of the given patient data strategy.

        Returns
        -------
        _patient_data_factory_instance : PatientDataQueryStrategy.factory
            Factory class instance used to get a patient's data.
        """
        _patient_data_factory_instance = self.patient_data_query_strategy.factory(
            images_data=self._images_data,
            organs=self._organs,
            paths_to_segmentations=self._paths_to_segmentations,
            series_descriptions=self._series_descriptions
        )

        return _patient_data_factory_instance

    def create_patient_data(self) -> PatientDataModel:
        """
        Creates a tuple containing all the patient's data.

        Returns
        -------
        patient_data: PatientDataModel
            Patient data.
        """
        return self._patient_data_factory_instance.create_patient_data()
