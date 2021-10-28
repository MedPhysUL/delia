from copy import deepcopy
import json
from collections.abc import Generator
from typing import Dict, List, Tuple, Union

from src.data_readers.patient_data_reader import PatientDataReader


class PatientDataGenerator(Generator):
    def __init__(
            self,
            paths_to_patients_folder_and_segmentations: List[Tuple[str, Union[List[str], None]]],
            series_descriptions: Dict[str, List[str]] = None,
            path_to_series_description_json: str = None
    ):
        self.paths_to_patients_folder_and_segmentations = paths_to_patients_folder_and_segmentations

        if series_descriptions and path_to_series_description_json:
            raise AssertionError("Either series descriptions or path to json has to be None.")
        elif not series_descriptions and path_to_series_description_json:
            self.path_to_series_description_json = path_to_series_description_json
        else:
            self.series_descriptions = series_descriptions

        self.idx = 0

    def __len__(self):
        return len(self.paths_to_patients_folder_and_segmentations)

    @property
    def series_descriptions(self):
        return self._series_descriptions

    @series_descriptions.setter
    def series_descriptions(self, series_descriptions: Dict[str, List[str]]):
        self._series_descriptions = series_descriptions

    @property
    def path_to_series_description_json(self):
        return self._path_to_series_description_json

    @path_to_series_description_json.setter
    def path_to_series_description_json(self, path_to_series_description_json: str):
        with open(path_to_series_description_json, "r") as json_file:
            self.series_descriptions = deepcopy(json.load(json_file))

        self._path_to_series_description_json = path_to_series_description_json

    def save_series_descriptions_to_json(self):
        with open(self.path_to_series_description_json, 'w', encoding='utf-8') as json_file:
            json.dump(self.series_descriptions, json_file, ensure_ascii=False, indent=4)

    def send(self, _):
        if self.idx == self.__len__():
            self.throw()

        path_to_dicom_folder = self.paths_to_patients_folder_and_segmentations[self.idx][0]
        paths_to_segmentation = self.paths_to_patients_folder_and_segmentations[self.idx][1]

        print("PATH: ", path_to_dicom_folder)
        print("SEG: ", paths_to_segmentation)

        patient_data_reader = PatientDataReader(
            path_to_dicom_folder=path_to_dicom_folder,
            paths_to_segmentation=paths_to_segmentation,
            series_descriptions=self.series_descriptions
        )
        self.series_descriptions = patient_data_reader.series_descriptions

        self.idx += 1

        return patient_data_reader.patient_dataset

    def throw(self, typ=None, value=None, traceback=None):
        raise StopIteration
