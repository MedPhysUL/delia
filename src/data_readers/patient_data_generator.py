"""
    @file:              patient_data_generator.py
    @Author:            Maxence Larose

    @Creation Date:     10/2021
    @Last modification: 10/2021

    @Description:       This file contains the PatientDataGenerator class which is used to iterate on multiple
                        patients' dicom files and segmentation files using the PatientDataReader to obtain all patients'
                        data. The PatientDataGenerator inherits from the Generator abstract class.
"""

from collections.abc import Generator
from copy import deepcopy
import json
from typing import Dict, List, NamedTuple, Optional, Union

from src.data_readers.patient_data_reader import PatientDataReader
from src.data_model import PatientDataModel


class PatientDataGenerator(Generator):
    """
    A class used to iterate on multiple patients' dicom files and segmentation files using the PatientDataReader to
    obtain all patients' data. The PatientDataGenerator inherits from the Generator abstract class.
    """

    class PathsToPatientFolderAndSegmentations(NamedTuple):
        """
        Namedtuple of paths to patient folder and segmentations.
        """
        path_to_patient_folder: Optional[str] = None
        path_to_segmentations: Optional[List[str]] = None

    def __init__(
            self,
            paths_to_patients_folder_and_segmentations: List[PathsToPatientFolderAndSegmentations],
            series_descriptions: Optional[Dict[str, List[str]]] = None,
            path_to_series_description_json: Optional[str] = None
    ):
        """
        Used to check if either the series descriptions or the path to the series description json dictionary is None.

        Parameters
        ----------
        paths_to_patients_folder_and_segmentations : List[PathsToPatientFolderAndSegmentations]
            List of named tuples including the path to the folder containing the patient dicom files and the path to
            the segmentations related to these dicom files.
        series_descriptions : Optional[Dict[str, List[str]]]
            A dictionary that contains the series descriptions of the images that absolutely needs to be extracted from
            the patient's file. Keys are arbitrary names given to the images we want to add and values are lists of
            series descriptions. The images associated with these series descriptions do not need to have a
            corresponding segmentation. In fact, the whole point of adding a way to specify the series descriptions that
            must be added to the dataset is to be able to add images without segmentation.
        path_to_series_description_json : Optional[str]
            Path to the json dictionary that contains the series descriptions.
        """
        self.paths_to_patients_folder_and_segmentations = paths_to_patients_folder_and_segmentations

        if series_descriptions and path_to_series_description_json:
            raise AssertionError("Either series descriptions or path to json has to be None.")
        elif not series_descriptions and path_to_series_description_json:
            self.path_to_series_description_json = path_to_series_description_json
        else:
            self.series_descriptions = series_descriptions
            self._path_to_series_description_json = None

        self.current_index = 0

    def __len__(self) -> int:
        """
        Total number of patients.

        Returns
        _______
        length: int
            Total number of patients.
        """
        return len(self.paths_to_patients_folder_and_segmentations)

    @property
    def series_descriptions(self) -> Dict[str, List[str]]:
        """
        Series descriptions.

        Returns
        -------
        series_descriptions : Dict[str, List[str]]
            A dictionary that contains the series descriptions of the images that absolutely needs to be extracted from
            the patient's file. Keys are arbitrary names given to the images we want to add and values are lists of
            series descriptions. The images associated with these series descriptions do not need to have a
            corresponding segmentation. In fact, the whole point of adding a way to specify the series descriptions that
            must be added to the dataset is to be able to add images without segmentation.
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
            must be added to the dataset is to be able to add images without segmentation.
        """
        self._series_descriptions = series_descriptions

    @property
    def path_to_series_description_json(self) -> Union[str, None]:
        """
        Path to series description json.

        Returns
        -------
        path_to_series_description_json : Union[str, None]
            Path to the json dictionary that contains the series descriptions.
        """
        return self._path_to_series_description_json

    @path_to_series_description_json.setter
    def path_to_series_description_json(self, path_to_series_description_json: str):
        """
        Path to series description json setter. This is used to set the series descriptions attribute using the
        dictionary read from the json file.

        Parameters
        ----------
        path_to_series_description_json : str
            Path to the json dictionary that contains the series descriptions.
        """
        with open(path_to_series_description_json, "r") as json_file:
            self.series_descriptions = deepcopy(json.load(json_file))

        self._path_to_series_description_json = path_to_series_description_json

    def save_series_descriptions_to_json(self, path: str):
        """
        Save the dictionary of series descriptions in a json format at the given path.

        Parameters
        ----------
        path : str
            Path to the json dictionary that will contain the series descriptions.
        """
        with open(path, 'w', encoding='utf-8') as json_file:
            json.dump(self.series_descriptions, json_file, ensure_ascii=False, indent=4)

    def send(self, _) -> PatientDataModel:
        """
        Resumes the execution and sends a value into the generator function. This method returns the next value yielded
        by the generator and update the current index or raises StopIteration (via the self.throw method) if all patient
        datasets have been generated.

        Returns
        -------
        patient_dataset : PatientDataModel
            A named tuple grouping the patient's data extracted from its dicom files and the patient's medical image
            segmentation data extracted from the segmentation files.
        """
        if self.current_index == self.__len__():
            self.throw()

        path_to_dicom_folder = self.paths_to_patients_folder_and_segmentations[self.current_index][0]
        paths_to_segmentation = self.paths_to_patients_folder_and_segmentations[self.current_index][1]

        patient_data_reader = PatientDataReader(
            path_to_dicom_folder=path_to_dicom_folder,
            paths_to_segmentation=paths_to_segmentation,
            series_descriptions=self.series_descriptions
        )
        self.series_descriptions = patient_data_reader.series_descriptions
        self.current_index += 1

        return patient_data_reader.get_patient_dataset()

    def throw(self, typ=StopIteration, value=None, traceback=None) -> None:
        """
        Raises an exception of type typ.
        """
        raise typ
