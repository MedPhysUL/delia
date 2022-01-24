"""
    @file:              patient_data_query_context.py
    @Author:            Maxence Larose

    @Creation Date:     01/2022
    @Last modification: 01/2022

    @Description:       This file contains the class PatientDataQueryContext that is used as a context class where
                        strategies are types of requests the client could ask the PatientDataReader class.
"""

from typing import Dict, List, Optional

from ...data_model import PatientDataModel
from .patient_data_query_strategy import PatientDataQueryStrategy, PatientDataQueryStrategies


class PatientDataQueryContext:
    """
    A class used as a context class where strategies are types of requests the client could make to the
    PatientDataReader class to get the patient's data.
    """

    def __init__(
            self,
            path_to_images_folder: str,
            path_to_segmentations_folder: Optional[str],
            series_descriptions: Dict[str, List[str]],
            verbose: bool
    ):
        """
        Constructor of the PatientDataQueryContext class.

        Parameters
        ----------
        path_to_images_folder : str
            Path to the folder containing the patient's image files.
        path_to_segmentations_folder : Optional[str]
            Path to the folder containing the patient's segmentation files.
        series_descriptions : Dict[str, List[str]]
            A dictionary that contains the series descriptions of the images that absolutely needs to be extracted from
            the patient's file. Keys are arbitrary names given to the images we want to add and values are lists of
            series descriptions. The images associated with these series descriptions do not need to have a
            corresponding segmentation. In fact, the whole point of adding a way to specify the series descriptions that
            must be added to the dataset is to be able to add images without segmentation.
        verbose : bool
            True to log/print some information else False.
        """
        self._path_to_images_folder = path_to_images_folder
        self._path_to_segmentations_folder = path_to_segmentations_folder
        self._series_descriptions = series_descriptions
        self._verbose = verbose

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
        if self._path_to_segmentations_folder and self._series_descriptions:
            return PatientDataQueryStrategies.SEGMENTATION_AND_SERIES_DESCRIPTION.value
        elif not self._path_to_segmentations_folder and self._series_descriptions:
            return PatientDataQueryStrategies.SERIES_DESCRIPTION.value
        elif self._path_to_segmentations_folder and not self._series_descriptions:
            return PatientDataQueryStrategies.SEGMENTATION.value
        else:
            return PatientDataQueryStrategies.DEFAULT.value

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
            path_to_images_folder=self._path_to_images_folder,
            path_to_segmentations_folder=self._path_to_segmentations_folder,
            series_descriptions=self._series_descriptions,
            verbose=self._verbose
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
