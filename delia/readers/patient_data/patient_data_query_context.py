"""
    @file:              patient_data_query_context.py
    @Author:            Maxence Larose

    @Creation Date:     01/2022
    @Last modification: 03/2022

    @Description:       This file contains the class PatientDataQueryContext that is used as a context class where
                        strategies are types of requests the client could ask the PatientDataReader class.
"""

from typing import Dict, List, Optional, Tuple, Union

from delia.utils.data_model import PatientDataModel
from .patient_data_query_strategy import PatientDataQueryStrategy, PatientDataQueryStrategies


class PatientDataQueryContext:
    """
    A class used as a context class where strategies are types of requests the client could make to the
    PatientDataReader class to get the patient's data.
    """

    def __init__(
            self,
            path_to_patient_folder: str,
            paths_to_segmentations: Optional[List[str]],
            tag_values: Dict[str, List[str]],
            tag: Union[str, Tuple[int, int]],
            organs: Optional[List[str]] = None,
            erase_unused_dicom_files: bool = False
    ):
        """
        Constructor of the PatientDataQueryContext class.

        Parameters
        ----------
        path_to_patient_folder : str
            Path to the folder containing the patient's DICOM files.
        paths_to_segmentations : Optional[List[str]]
            List of paths to the patient's segmentation files.
        tag_values : Dict[str, List[str]]
            A dictionary that contains the desired tag's values for the images that absolutely needs to be extracted
            from the patient's file. Keys are arbitrary names given to the images we want to add and values are lists of
            values associated with the specified tag.
        tag : Union[str, Tuple[int, int]]
            Keyword or tuple of the DICOM tag to use while selecting which files to extract.
        organs : Optional[List[str]]
            A set of the organs to save.
        erase_unused_dicom_files: bool = False
            Whether to delete unused DICOM files or not. Use with caution.
        """
        self._path_to_patient_folder = path_to_patient_folder
        self._paths_to_segmentations = paths_to_segmentations
        self._tag_values = tag_values
        self._organs = organs
        self._erase_unused_dicom_files = erase_unused_dicom_files
        self.tag = tag

    @property
    def patient_data_query_strategy(self) -> PatientDataQueryStrategy:
        """
        Patient data query strategy corresponding to the given tag values configuration.

        Returns
        -------
        patient_data_query_strategy : PatientDataQueryStrategy
            Patient data query strategy.
        """
        if self._tag_values:
            return PatientDataQueryStrategies.TAG_VALUE.value
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
        patient_data_factory_instance = self.patient_data_query_strategy.factory(
            path_to_patient_folder=self._path_to_patient_folder,
            paths_to_segmentations=self._paths_to_segmentations,
            tag_values=self._tag_values,
            tag=self.tag,
            organs=self._organs,
            erase_unused_dicom_files=self._erase_unused_dicom_files
        )

        return patient_data_factory_instance

    def create_patient_data(self) -> PatientDataModel:
        """
        Creates a tuple containing all the patient's data.

        Returns
        -------
        patient_data: PatientDataModel
            Patient data.
        """
        return self._patient_data_factory_instance.create_patient_data()
