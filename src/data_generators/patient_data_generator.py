"""
    @file:              patient_data_generator.py
    @Author:            Maxence Larose

    @Creation Date:     10/2021
    @Last modification: 01/2022

    @Description:       This file contains the PatientDataGenerator class which is used to iterate on multiple
                        patients' dicom files and segmentation files using the PatientDataReader to obtain all patients'
                        data. The PatientDataGenerator inherits from the Generator abstract class.
"""

from collections.abc import Generator
from copy import deepcopy
import json
import logging
from typing import Dict, List, NamedTuple, Optional, Union

from ..data_readers.patient_data.patient_data_reader import PatientDataReader
from ..data_model import PatientDataModel


class PatientDataGenerator(Generator):
    """
    A class used to iterate on multiple patients' dicom files and segmentation files using the PatientDataReader to
    obtain all patients' data. The PatientDataGenerator inherits from the Generator abstract class.
    """

    class PathsToPatientFolderAndSegmentations(NamedTuple):
        """
        Namedtuple of paths to patient folder and segmentations.
        """
        path_to_patient_folder: str
        path_to_segmentations: Optional[List[str]] = None

    def __init__(
            self,
            paths_to_patients_folder_and_segmentations: List[PathsToPatientFolderAndSegmentations],
            verbose: bool,
            organs: Optional[Union[str, Dict[str, List[str]]]] = None,
            series_descriptions: Optional[Union[str, Dict[str, List[str]]]] = None,
    ):
        """
        Used to check if either the series descriptions or the path to the series description json dictionary is None.

        Parameters
        ----------
        paths_to_patients_folder_and_segmentations : List[PathsToPatientFolderAndSegmentations]
            List of named tuples including the path to the folder containing the patient dicom files and the path to
            the segmentations related to these dicom files.
        verbose : bool
            True to log/print some information else False.
        organs : Optional[Union[str, Dict[str, List[str]], None]], default = None.
            A dictionary that contains the organs and their associated segment names. Keys are arbitrary organ names
            and values are lists of possible segment names. It can also be specified as a path to a json file that
            contains the organs dictionary.
        series_descriptions : Optional[Union[str, Dict[str, List[str]], None]], default = None.
            A dictionary that contains the series descriptions of the images that absolutely needs to be extracted from
            the patient's file. Keys are arbitrary names given to the images we want to add and values are lists of
            series descriptions. The images associated with these series descriptions do not need to have a
            corresponding segmentation. In fact, the whole point of adding a way to specify the series descriptions that
            must be added to the dataset is to be able to add images without their segmentation. Can be specified as a
            path to a json file that contains the series descriptions dictionary.
        """
        self.paths_to_patients_folder_and_segmentations = paths_to_patients_folder_and_segmentations

        if isinstance(series_descriptions, str):
            self.path_to_series_description_json = series_descriptions
        elif isinstance(series_descriptions, dict):
            self.series_descriptions = series_descriptions
            self.path_to_series_description_json = None
        elif series_descriptions is None:
            self.series_descriptions = None
            self.path_to_series_description_json = None
        else:
            raise TypeError(f"Given series descriptions {series_descriptions} doesn't have the right type. Allowed"
                            f" types are str, dict and None.")

        if isinstance(organs, str):
            self.path_to_organs_json = organs
        elif isinstance(organs, dict):
            self.organs = organs
            self.path_to_organs_json = None
        elif organs is None:
            if any(paths.path_to_segmentations for paths in self.paths_to_patients_folder_and_segmentations):
                raise AssertionError("The variable organs is required. It is a dictionary where keys are arbitrary"
                                     " organ names and values are lists of possible segment names.")
            self.organs = None
            self.path_to_organs_json = None
        else:
            raise TypeError(f"Given organs {organs} doesn't have the right type. Allowed types are str, dict and None.")

        self._verbose = verbose
        self.current_index = 0

        if verbose:
            logging.info(f"\n# {'-'*111} #\n# {' ' * 40} DOWNLOADING ALL PATIENTS DATA {' ' * 40} #\n# {'-'*111} #")

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
    def series_descriptions(self, series_descriptions: Dict[str, List[str]]) -> None:
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
        items = list(series_descriptions.items())
        for previous_items, current_items in zip(items, items[1:]):
            set_intersection = set(previous_items[1]) & set(current_items[1])

            if bool(set_intersection):
                raise AssertionError(f"\nThe dictionary of series descriptions should not contain the same series names"
                                     f" for different images/modalities. \nHowever, here we find the series names "
                                     f"{previous_items[1]} for the {previous_items[0]} image and {current_items[1]} "
                                     f"for the {current_items[0]} image. \nClearly, the images series values are "
                                     f"overlapping because of the series named {set_intersection}.")

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
    def path_to_series_description_json(self, path_to_series_description_json: str) -> None:
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

    def save_series_descriptions_to_json(self, path: str) -> None:
        """
        Save the dictionary of series descriptions in a json format at the given path.

        Parameters
        ----------
        path : str
            Path to the json dictionary that will contain the series descriptions.
        """
        with open(path, 'w', encoding='utf-8') as json_file:
            json.dump(self.series_descriptions, json_file, ensure_ascii=False, indent=4)

    @property
    def organs(self) -> Dict[str, List[str]]:
        """
        Organs property.

        Returns
        -------
        organs : Dict[str, List[str]]
            A dictionary that contains the organs and their associated segment names. Keys are arbitrary organ names
            and values are the list of possible segment names for each organ.
        """
        return self._organs

    @organs.setter
    def organs(self, organs: Dict[str, List[str]]) -> None:
        """
        Organs setter.

        Parameters
        ----------
        organs : Dict[str, List[str]]
            A dictionary that contains the organs and their associated segment names. Keys are arbitrary organ names
            and values are the list of possible segment names for each organ.
        """
        self._organs = organs

    @property
    def path_to_organs_json(self) -> str:
        """
        Path to organs json property.

        Returns
        -------
        path_to_organs_json : str
            Path to a json dictionary that contains the list of possible segment names for each organ. Keys are
            arbitrary organ names and values are the list of possible segment names for each organ.
        """
        return self._path_to_series_description_json

    @path_to_organs_json.setter
    def path_to_organs_json(self, path_to_organs_json: str) -> None:
        """
        Path to organs json setter.

        Parameters
        ----------
        path_to_organs_json : str
            Path to a json dictionary that contains the list of possible segment names for each organ. Keys are
            arbitrary organ names and values are the list of possible segment names for each organ.
        """
        with open(path_to_organs_json, "r") as json_file:
            self.organs = deepcopy(json.load(json_file))

        self._path_to_organs_json = path_to_organs_json

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
        paths_to_segmentations = self.paths_to_patients_folder_and_segmentations[self.current_index][1]

        if self._verbose:
            logging.info(f"\n\n# {'-'*50} Patient {self.current_index + 1} {'-'*50} #")

        patient_data_reader = PatientDataReader(
            path_to_dicom_folder=path_to_dicom_folder,
            verbose=self._verbose,
            organs=self.organs,
            paths_to_segmentations=paths_to_segmentations,
            series_descriptions=self.series_descriptions
        )
        self.series_descriptions = patient_data_reader.series_descriptions
        if self.path_to_series_description_json:
            self.save_series_descriptions_to_json(path=self._path_to_series_description_json)
        self.current_index += 1

        return patient_data_reader.get_patient_dataset()

    def throw(self, typ=StopIteration, value=None, traceback=None) -> None:
        """
        Raises an exception of type typ.
        """
        raise typ
