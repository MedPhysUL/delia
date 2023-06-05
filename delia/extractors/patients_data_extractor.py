"""
    @file:              patients_data_generator.py
    @Author:            Maxence Larose

    @Creation Date:     10/2021
    @Last modification: 10/2022

    @Description:       This file contains the PatientsDataGenerator class which is used to iterate on multiple
                        patients' dicom files and segmentation files using the PatientDataReader to obtain all patients'
                        data. The PatientsDataGenerator inherits from the Generator abstract class.
"""

from collections.abc import Generator
from copy import deepcopy
import json
import logging
import os
from typing import Dict, List, NamedTuple, Optional, Union, Tuple

from monai.transforms import Compose
from monai.transforms import MapTransform as MonaiMapTransform
from pydicom.datadict import keyword_for_tag

from delia.readers.patient_data.patient_data_reader import PatientDataReader
from delia.transforms.data.transform import DataTransform
from delia.transforms.physical_space.transform import PhysicalSpaceTransform
from delia.utils.data_model import PatientDataModel

_logger = logging.getLogger(__name__)


class PatientWhoFailed(NamedTuple):
    id: str
    failed_images: Dict[str, List[str]]
    available_series_descriptions: List[str]


class PatientsDataExtractor(Generator):
    """
    A class used to iterate on multiple patients' dicom files and segmentation files using the PatientDataReader to
    obtain all patients' data. The PatientsDataGenerator inherits from the Generator abstract class.
    """

    def __init__(
            self,
            path_to_patients_folder: str,
            tag: Union[str, Tuple[int, int]] = "SeriesDescription",
            series_descriptions: Optional[Union[str, Dict[str, List[str]]]] = None,
            transforms: Optional[Union[Compose, DataTransform, MonaiMapTransform, PhysicalSpaceTransform]] = None,
            erase_unused_dicom_files: bool = False
    ) -> None:
        """
        Used to get the paths to the images and segmentations folders. Also used to check if either the series
        descriptions or the path to the series description json dictionary is None.

        Parameters
        ----------
        path_to_patients_folder : str
            The path to the folder that contains all the patients' folders.
        tag : Union[str, Tuple[int, int]] = "SeriesDescription"
            Keyword or tuple of the DICOM tag to use while selecting which files to extract. Uses SeriesDescription
             as a default.
        series_descriptions : Optional[Union[str, Dict[str, List[str]]]], default = None.
            A dictionary that contains the series descriptions of the images that needs to be extracted from the
            patient's file. Keys are arbitrary names given to the images we want to add and values are lists of
            series descriptions. The images associated with these series descriptions do not need to have a
            corresponding segmentation. Note that it can be specified as a path to a json dictionary that contains the
            series descriptions.
        transforms : Union[Compose, DataTransform, MonaiMapTransform, PhysicalSpaceTransform]
            A sequence of transformations to apply. PhysicalSpaceTransform are applied in the physical space, i.e on
            the SimpleITK image, while MonaiMapTransform are applied in the array space, i.e on the numpy array that
            represents the image. DataTransform transforms the data using other a patient's other images or
            segmentations. The keys for images are assumed to be the arbitrary series key set in 'series_descriptions'.
            For segmentation, keys are organ names. Note that if 'series_descriptions' is None, the keys for images are
            assumed to be modalities.
        erase_unused_dicom_files: bool = False
            Whether to delete unused DICOM files or not. Use with EXTREME caution!
        """
        self._path_to_patients_folder = path_to_patients_folder
        self._erase_unused_dicom_files = erase_unused_dicom_files
        self._transforms = self._validate_transforms(transforms)
        self.tag = tag

        if isinstance(series_descriptions, str):
            self.path_to_series_description_json = series_descriptions
        elif isinstance(series_descriptions, dict):
            self.series_descriptions = series_descriptions
            self._path_to_series_description_json = None
        elif series_descriptions is None:
            self._series_descriptions = None
            self._path_to_series_description_json = None
        else:
            raise TypeError(
                f"Given series descriptions {series_descriptions} doesn't have the right type. Allowed types are str, "
                f"dict and None."
            )

        self._current_index = 0
        self._patients_who_failed = []

    def __len__(self) -> int:
        """
        Total number of patients.

        Returns
        -------
        length: int
            Total number of patients.
        """
        return len(self.paths_to_patients_folders)

    @property
    def paths_to_patients_folders(self) -> List[str]:
        """
        Get a list of paths to the patients' folders.

        Returns
        -------
        paths_to_patients_folders : List[str]
            A list of paths to the folders containing the patients' data.
        """
        paths_to_folders = []
        for patient_folder_name in os.listdir(self._path_to_patients_folder):
            path_to_folder = os.path.join(
                self._path_to_patients_folder,
                patient_folder_name
            )
            paths_to_folders.append(path_to_folder)

        return paths_to_folders

    @property
    def series_descriptions(self) -> Dict[str, List[str]]:
        """
        Series descriptions.

        Returns
        -------
        series_descriptions : Dict[str, List[str]]
            A dictionary that contains the series descriptions of the images that absolutely needs to be extracted from
            the patient's file. Keys are arbitrary names given to the images we want to add and values are lists of
            series descriptions.
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
            series descriptions.
        """
        items = list(series_descriptions.items())
        for previous_items, current_items in zip(items, items[1:]):
            set_intersection = set(previous_items[1]) & set(current_items[1])

            if bool(set_intersection):
                raise AssertionError(
                    f"\nThe dictionary of series descriptions should not contain the same series names for different "
                    f"images/modalities. \nHowever, here we find the series names {previous_items[1]} for the "
                    f"{previous_items[0]} image and {current_items[1]} for the {current_items[0]} image. \nClearly, "
                    f"the images series values are overlapping because of the series named {set_intersection}."
                )

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

    @property
    def patients_who_failed(self) -> List[PatientWhoFailed]:
        """
        List of patients with one or more images not added to the HDF5 dataset due to the absence of the series in
        the patient record.

        Returns
        -------
        patients_who_failed : List[PatientWhoFailed]
            List of patients with one or more images not added to the HDF5 dataset due to the absence of the series in
            the patient record.
        """
        return self._patients_who_failed

    @staticmethod
    def _validate_transforms(
            transforms: Union[Compose, DataTransform, PhysicalSpaceTransform, MonaiMapTransform]
    ) -> Optional[Union[Compose, DataTransform, PhysicalSpaceTransform, MonaiMapTransform]]:
        """
        Validate transforms type and set allow_missing_keys attributes to True.

        Parameters
        ----------
        transforms : Union[Compose, DataTransform, MonaiMapTransform, PhysicalSpaceTransform]
            A sequence of transformations to apply. PhysicalSpaceTransform are applied in the physical space, i.e on
            the SimpleITK image, while MonaiMapTransform are applied in the array space, i.e on the numpy array that
            represents the image. DataTransform transforms the data using other a patient's other images or
            segmentations. The keys for images are assumed to be the arbitrary series key set in 'series_descriptions'.
            For segmentation, keys are organ names. Note that if 'series_descriptions' is None, the keys for images are
            assumed to be modalities.

        Returns
        -------
        transforms : Union[Compose, DataTransform, MonaiMapTransform, PhysicalSpaceTransform]
            A sequence of transformations to apply. PhysicalSpaceTransform are applied in the physical space, i.e on
            the SimpleITK image, while MonaiMapTransform are applied in the array space, i.e on the numpy array that
            represents the image. DataTransform transforms the data using other a patient's other images or
            segmentations. The keys for images are assumed to be the arbitrary series key set in 'series_descriptions'.
            For segmentation, keys are organ names. Note that if 'series_descriptions' is None, the keys for images are
            assumed to be modalities.
        """
        if transforms is None:
            return transforms
        elif isinstance(transforms, Compose):
            for t in transforms.transforms:
                if not isinstance(t, (DataTransform, PhysicalSpaceTransform, MonaiMapTransform)):
                    raise AssertionError(
                        "The given transforms must inherit from 'DataTransform', 'PhysicalSpaceTransform' or "
                        "'MonaiMapTransform'."
                    )
                t.allow_missing_keys = True
            return transforms
        elif isinstance(transforms, (DataTransform, PhysicalSpaceTransform, MonaiMapTransform)):
            transforms.allow_missing_keys = True
            return transforms
        else:
            raise AssertionError(
                "'transforms' must either be of type 'Compose', 'DataTransform', 'PhysicalSpaceTransform' or "
                "'MonaiMapTransform'."
            )

    def save_series_descriptions_to_json(self, path: str) -> None:
        """
        Saves the dictionary of series descriptions in a json format at the given path.

        Parameters
        ----------
        path : str
            Path to the json dictionary that will contain the series descriptions.
        """
        with open(path, 'w', encoding='utf-8') as json_file:
            json.dump(self.series_descriptions, json_file, ensure_ascii=False, indent=4)

    def reset(self) -> None:
        """
        Resets the generator.
        """
        self._current_index = 0
        self._patients_who_failed = []

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
        if self._current_index == len(self):
            self.throw()

        _logger.info(f"Downloading Patient {self._current_index + 1}/{len(self)}")
        _logger.info(f"Path to patient folder : {self.paths_to_patients_folders[self._current_index]}")

        patient_data_reader = PatientDataReader(
            path_to_patient_folder=self.paths_to_patients_folders[self._current_index],
            series_descriptions=self.series_descriptions,
            tag=self.tag,
            erase_unused_dicom_files=self._erase_unused_dicom_files
        )

        if self._series_descriptions is not None:
            self.series_descriptions = patient_data_reader.series_descriptions
        if self.path_to_series_description_json:
            self.save_series_descriptions_to_json(path=self._path_to_series_description_json)
        if patient_data_reader.failed_images:
            failed_images = {image: self.series_descriptions[image] for image in patient_data_reader.failed_images}

            self._patients_who_failed.append(
                PatientWhoFailed(
                    id=patient_data_reader.patient_id,
                    failed_images=failed_images,
                    available_series_descriptions=patient_data_reader.available_series_descriptions
                )
            )

        self._current_index += 1

        return patient_data_reader.get_patient_dataset(transforms=self._transforms)

    def throw(self, typ: Exception = StopIteration, value=None, traceback=None) -> None:
        """
        Raises an exception of type typ.
        """
        raise typ
