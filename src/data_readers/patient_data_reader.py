import enum
import itertools
import logging
import warnings
from typing import Callable, Dict, List, NamedTuple, Union

import json

from src.data_model import ImageAndSegmentationDataModel, SegmentationDataModel, PatientDataModel
from .dicom_reader import DicomReader
from .segmentation_reader import SegmentationReader
from src.constants.segmentation_category import SegmentationCategory


class PatientDataReader(DicomReader, SegmentationReader):
    class QueryTypeName(enum.Enum):
        DEFAULT = "Default"
        SEGMENTATION = "Segmentation"
        SERIES_DESCRIPTION = "Series description"
        SEGMENTATION_AND_SERIES_DESCRIPTION = "Segmentation and series description"

    class QueryTypeFunction(NamedTuple):
        DEFAULT: Callable = None
        SEGMENTATION: Callable = None
        SERIES_DESCRIPTION: Callable = None
        SEGMENTATION_AND_SERIES_DESCRIPTION: Callable = None

    def __init__(
            self,
            path_to_dicom_folder: str,
            paths_to_segmentation: List[str] = None,
            series_descriptions: Dict[str, List[str]] = None
    ):
        """
        Used to load one or multiple patients' dicom and segmentation files and associate those together.

        Parameters
        ----------
        path_to_dicom_folder : str
            Path to the folder containing the patient dicom files.
        paths_to_segmentation : List[List[str]]
            Path to the folder containing all segmentations.

        Attributes
        ----------
        self.patient_dataset : PatientDataModel
            A dictionary regrouping the patient data retrieved from his dicom files and the segmentation data retrieved
            from the segmentation and mask files.
        """
        super(PatientDataReader, self).__init__()
        self.path_to_dicom_folder = path_to_dicom_folder
        self.paths_to_segmentation = paths_to_segmentation
        self._series_descriptions = series_descriptions

        self._patient_image_data = self._get_patient_image_data(path_to_dicom_folder=path_to_dicom_folder)

        self.check_availability_of_given_segmentations_uid()
        self.check_availability_of_given_series_description()

    @property
    def series_descriptions(self):
        return self._series_descriptions

    @series_descriptions.setter
    def series_descriptions(self, series_descriptions: Dict[str, List[str]]):
        self._series_descriptions = series_descriptions

    @property
    def flatten_series_descriptions(self):
        return [val for lst in self.series_descriptions.values() for val in lst]

    def available_series_descriptions(self):
        available_series_descriptions = [
            image_data.image.dicom_header.SeriesDescription for image_data in self._patient_image_data.data
        ]

        return available_series_descriptions

    def available_series_uid(self):
        available_series_uid = [
            image_data.image.dicom_header.SeriesInstanceUID for image_data in self._patient_image_data.data
        ]

        return available_series_uid

    def update_series_descriptions(self, series_key):
        logging.info(f"No available series for {series_key}. Available series are "
                     f"{self.available_series_descriptions()}. Choose one :")
        while True:
            new_series_description = input()

            if new_series_description in self.available_series_descriptions():
                break
            else:
                logging.info("Try again.")

        self.series_descriptions[series_key] += [new_series_description]

    def check_availability_of_given_series_description(self):
        for series_key, series_description_list in self.series_descriptions.items():
            if any(series in self.available_series_descriptions() for series in series_description_list):
                pass
            else:
                self.update_series_descriptions(series_key)
                self.check_availability_of_given_series_description()

    def check_availability_of_given_segmentations_uid(self):
        for path_to_segmentation in self.paths_to_segmentation:
            if any(uid in path_to_segmentation for uid in self.available_series_uid()):
                pass
            else:
                warnings.warn("no uid for given segmentation")

    def default_query(self):
        return self._patient_image_data

    def segmentation_specific_query(self):
        data = []
        for image_data in self._patient_image_data.data:
            image = image_data.image
            for path_to_segmentation in self.paths_to_segmentation:
                if image_data.image.dicom_header.SeriesInstanceUID in path_to_segmentation:
                    image_and_segmentation_data = ImageAndSegmentationDataModel(
                        image=image,
                        segmentation=self.get_segmentation_data(path_to_segmentation=path_to_segmentation)
                    )

                    data.append(image_and_segmentation_data)

        return data

    def series_description_specific_query(self):
        data = []
        for image_idx, image_data in enumerate(self._patient_image_data.data):
            if image_data.image.dicom_header.SeriesDescription in self.flatten_series_descriptions:
                data.append(image_data)

        return data

    def segmentation_and_series_description_specific_query(self):
        data = []
        for image_idx, image_data in enumerate(self._patient_image_data.data):
            image_added = False
            for path_to_segmentation in self.paths_to_segmentation:
                if image_data.image.dicom_header.SeriesInstanceUID in path_to_segmentation:
                    image_and_segmentation_data = ImageAndSegmentationDataModel(
                        image=image_data.image,
                        segmentation=self.get_segmentation_data(path_to_segmentation=path_to_segmentation)
                    )
                    data.append(image_and_segmentation_data)
                    image_added = True

            series_description = image_data.image.dicom_header.SeriesDescription
            if series_description in self.flatten_series_descriptions and image_added is False:
                data.append(image_data)

        return data

    def query_functions(self):
        query_functions = self.QueryTypeFunction(
            DEFAULT=self.default_query,
            SEGMENTATION=self.segmentation_specific_query,
            SERIES_DESCRIPTION=self.series_description_specific_query,
            SEGMENTATION_AND_SERIES_DESCRIPTION=self.segmentation_and_series_description_specific_query
        )

        return query_functions

    @property
    def patient_name(self):
        patient_name = self._patient_image_data.patient_name

        return patient_name

    @property
    def query_type(self) -> QueryTypeName:
        if self.paths_to_segmentation and self.series_descriptions:
            return self.QueryTypeName.SEGMENTATION_AND_SERIES_DESCRIPTION
        elif self.paths_to_segmentation is None and self.series_descriptions:
            return self.QueryTypeName.SERIES_DESCRIPTION
        elif self.paths_to_segmentation and self.series_descriptions is None:
            return self.QueryTypeName.SEGMENTATION
        else:
            return self.QueryTypeName.DEFAULT

    @property
    def query_function(self) -> Callable:
        return getattr(self.query_functions(), self.query_type.name)

    def _get_patient_data(self) -> Dict[str, ImageAndSegmentationDataModel]:
        """
        Get patient data.

        Returns
        -------
        data : Dict[str, ImageAndSegmentationDataModel]
            Dictionary containing the patient's data extracted from its dicom files and the patient's medical image
            segmentation data extracted from the segmentation files, for each available modality. This dictionary is
            formatted as follows :

                data: {
                    modality (example: "CT"): (
                        "image" : ImageDataModel,
                        "segmentation" : SegmentationDataModel,
                    ),
                    modality (example: "PT"): (
                        "image" : ImageDataModel,
                        "segmentation" : SegmentationDataModel,
                    ),
                    ...
                }
        """
        pass

    @property
    def patient_dataset(
            self,
    ) -> PatientDataModel:
        """
        Patient dataset.

        Returns
        -------
        patient_dataset : PatientDataModel
            A named tuple grouping the patient's data extracted from its dicom files and the patient's medical image
            segmentation data extracted from the segmentation files, for each available modality.
        """
        patient_dataset = PatientDataModel(
            patient_name=self.patient_name,
            data=self.query_function()
        )

        return patient_dataset
