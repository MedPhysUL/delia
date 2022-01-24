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
import os
from typing import Dict, List, Optional, Union

from ..data_readers.patient_data.patient_data_reader import PatientDataReader
from ..data_model import PatientDataModel


class PatientDataGenerator(Generator):
    """
    A class used to iterate on multiple patients' dicom files and segmentation files using the PatientDataReader to
    obtain all patients' data. The PatientDataGenerator inherits from the Generator abstract class.
    """

    def __init__(
            self,
            path_to_patients_folder: str,
            images_folder_name: str = "images",
            segmentations_folder_name: str = "segmentations",
            series_descriptions: Optional[Union[str, Dict[str, List[str]]]] = None,
            verbose: bool = True,
    ):
        """
        Used to check if either the series descriptions or the path to the series description json dictionary is None.

        Parameters
        ----------
        path_to_patients_folder : str
            The path to the folder that contains all the patients' folders.
        images_folder_name : str, default = "images".
            Images folder name.
        segmentations_folder_name : str, default = "segmentations".
            Segmentations folder name.
        series_descriptions : Optional[Union[str, Dict[str, List[str]], None]], default = None.
            A dictionary that contains the series descriptions of the images that absolutely needs to be extracted from
            the patient's file. Keys are arbitrary names given to the images we want to add and values are lists of
            series descriptions. The images associated with these series descriptions do not need to have a
            corresponding segmentation. In fact, the whole point of adding a way to specify the series descriptions that
            must be added to the dataset is to be able to add images without their segmentation. Can be specified as a
            path to a json file that contains the series descriptions dictionary.
        verbose : bool, default = True.
            True to log/print some information else False.
        """
        self._path_to_patients_folder = path_to_patients_folder
        self._paths_to_images_folder = self.get_paths_to_folder(images_folder_name)
        self._paths_to_segmentations_folder = self.get_paths_to_folder(segmentations_folder_name)

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

        self._verbose = verbose
        self._current_index = 0

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
        return len(self._paths_to_images_folder)

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

    def get_paths_to_folder(self, folder_name: str) -> List[str]:
        """
        Get a list of paths to the patients' folders that have the given folder name.

        Parameters
        ----------
        folder_name: str
            The name of a folder that is present in all patient folders.

        Returns
        -------
        paths_to_images_folder: List[str]
            A list of paths to the folders containing the patients' images.
        """
        paths_to_folder = []
        for patient_folder_name in os.listdir(self._path_to_patients_folder):
            path_to_folder = os.path.join(
                self._path_to_patients_folder,
                patient_folder_name,
                folder_name
            )
            paths_to_folder.append(path_to_folder)

        return paths_to_folder

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
        if self._current_index == self.__len__():
            self.throw()

        if self._verbose:
            logging.info(f"\n\n# {'-'*50} Patient {self._current_index + 1} {'-' * 50} #")

        patient_data_reader = PatientDataReader(
            path_to_images_folder=self._paths_to_images_folder[self._current_index],
            path_to_segmentations_folder=self._paths_to_segmentations_folder[self._current_index],
            series_descriptions=self.series_descriptions,
            verbose=self._verbose,
        )

        self.series_descriptions = patient_data_reader.series_descriptions
        if self.path_to_series_description_json:
            self.save_series_descriptions_to_json(path=self._path_to_series_description_json)
        self._current_index += 1

        return patient_data_reader.get_patient_dataset()

    def throw(self, typ=StopIteration, value=None, traceback=None) -> None:
        """
        Raises an exception of type typ.
        """
        raise typ
