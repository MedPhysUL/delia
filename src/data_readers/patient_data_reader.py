"""
    @file:              patient_data_reader.py
    @Author:            Maxence Larose

    @Creation Date:     10/2021
    @Last modification: 10/2021

    @Description:       This file contains the PatientDataReader class which is used to read dicom files AND
                        segmentation files to transform their contents into the format of the PatientDataModel class.
"""

import enum
import logging
from typing import Callable, Dict, List, NamedTuple, Optional

from src.data_model import ImageAndSegmentationDataModel, PatientDataModel
from .dicom_reader import DicomReader
from .segmentation_reader import SegmentationReader


class PatientDataReader(DicomReader):
    """
    A class used to read dicom files AND segmentation files to transform their contents into the format of the
    PatientDataModel class.
    """

    class QueryTypeName(enum.Enum):
        """
        Enumeration of the names of the different types of queries.
        """
        DEFAULT = "Default"
        SEGMENTATION = "Segmentation"
        SERIES_DESCRIPTION = "Series description"
        SEGMENTATION_AND_SERIES_DESCRIPTION = "Segmentation and series description"

    class QueryTypeFunction(NamedTuple):
        """
        Namedtuple of the functions associated to the different types of queries.
        """
        DEFAULT: Callable = None
        SEGMENTATION: Callable = None
        SERIES_DESCRIPTION: Callable = None
        SEGMENTATION_AND_SERIES_DESCRIPTION: Callable = None

    def __init__(
            self,
            path_to_dicom_folder: str,
            paths_to_segmentation: Optional[List[str]] = None,
            series_descriptions: Optional[Dict[str, List[str]]] = None
    ):
        """
        Used to check availability of given series' uid and series descriptions in the patient's dicom files.

        Parameters
        ----------
        path_to_dicom_folder : str
            Path to the folder containing the patient dicom files.
        paths_to_segmentation : Optional[List[str]]
            A list of paths to the segmentation files. The name of the segmentation files must include the series uid
            of their corresponding image, i.e. the image on which the segmentation was made.
        series_descriptions : Optional[Dict[str, List[str]]]
            A dictionary that contains the series descriptions of the images that absolutely needs to be extracted from
            the patient's file. Keys are arbitrary names given to the images we want to add and values are lists of
            series descriptions. The images associated with these series descriptions do not need to have a
            corresponding segmentation. In fact, the whole point of adding a way to specify the series descriptions that
            must be added to the dataset is to be able to add images without segmentation.
        """
        super(PatientDataReader, self).__init__(path_to_dicom_folder=path_to_dicom_folder)
        self._images_data = self.get_images_data()

        self.paths_to_segmentation = paths_to_segmentation
        self._series_descriptions = series_descriptions

        # self.check_availability_of_given_series_uids()
        # self.check_availability_of_given_series_description()

    @property
    def patient_name(self) -> str:
        """
        Patient name.

        Returns
        -------
        patient_name : str
            Patient name.
        """
        patient_name = self._images_data[0].dicom_header.PatientName

        return str(patient_name)

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
            must be added to the dataset is to be able to add images without segmentation. the patient dataset.
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
            must be added to the dataset is to be able to add images without segmentation. the patient dataset.
        """
        self._series_descriptions = series_descriptions

    @property
    def flatten_series_descriptions(self) -> List[str]:
        """
        Flatten series descriptions.

        Returns
        -------
        flatten_series_description : List[str]
            Series descriptions as a list instead of a dictionary.
        """
        return [val for lst in self.series_descriptions.values() for val in lst]

    @property
    def available_series_descriptions(self) -> List[str]:
        """
        Available series descriptions.

        Returns
        -------
        available_series_descriptions : List[str]
            Available series descriptions in the patient dicom files.
        """
        available_series_descriptions = [
            image.dicom_header.SeriesDescription for image in self._images_data
        ]

        return available_series_descriptions

    @property
    def available_series_uids(self) -> List[str]:
        """
        Available series' uids.

        Returns
        -------
        available_series_uids : List[str]
            Available series uids in the patient dicom files.
        """
        available_series_uid = [
            image.dicom_header.SeriesInstanceUID for image in self._images_data
        ]

        return available_series_uid

    def update_series_descriptions(self, series_key: str) -> None:
        """
        Add a series description to the series description list of the given series key.

        Parameters
        ----------
        series_key : str
            Series key.
        """
        logging.info(f"No available series for {series_key}. Available series are "
                     f"{self.available_series_descriptions}.")

        while True:
            new_series_description = input("Name of the series description to add: ")

            if new_series_description in self.available_series_descriptions:
                break
            else:
                logging.info(f"The given series description name is {new_series_description}. However, this is NOT one "
                             f"of the available series description found in the patient's dicom files. Available "
                             f"series are {self.available_series_descriptions}. Please try again.")

        self.series_descriptions[series_key] += [new_series_description]

    def check_availability_of_given_series_description(self) -> None:
        """
        Check availability of given series description in the patient's dicom files.
        """
        for series_key, series_description_list in self.series_descriptions.items():
            if any(series in self.available_series_descriptions for series in series_description_list):
                pass
            else:
                self.update_series_descriptions(series_key)
                self.check_availability_of_given_series_description()

    def check_availability_of_given_series_uids(self) -> None:
        """
        Check availability of given series uids in the patient's dicom files.
        """
        for path_to_segmentation in self.paths_to_segmentation:
            if any(uid in path_to_segmentation for uid in self.available_series_uids):
                pass
            else:
                logging.warning(f"The given segmentation file name is {path_to_segmentation}. However, this file name "
                                f"does NOT contain any of the available series uids found in the patient's dicom "
                                f"files. Available series uids are {self.available_series_uids}.")

    def default_query(self) -> List[ImageAndSegmentationDataModel]:
        """
        The default query consists in obtaining all the images without any segmentation.

        Returns
        -------
        image_data : List[ImageAndSegmentationDataModel]
            image_data
        """
        return [ImageAndSegmentationDataModel(image=image) for image in self._images_data]

    def segmentation_specific_query(self) -> List[ImageAndSegmentationDataModel]:
        """
        The segmentation specific query consists in obtaining the images that have the same serial uids as those
        contained in the file names of the given segmentations. The final dataset therefore contains both the
        segmentations and their corresponding images.

        Returns
        -------
        image_and_segmentation_data : List[ImageAndSegmentationDataModel]
            image_and_segmentation_data
        """
        data = []
        for image in self._images_data:
            for path_to_segmentation in self.paths_to_segmentation:
                if image.dicom_header.SeriesInstanceUID in path_to_segmentation:
                    segmentation_reader = SegmentationReader(path_to_segmentation=path_to_segmentation)

                    image_and_segmentation_data = ImageAndSegmentationDataModel(
                        image=image,
                        segmentation=segmentation_reader.get_segmentation_data()
                    )

                    data.append(image_and_segmentation_data)

        return data

    def series_description_specific_query(self) -> List[ImageAndSegmentationDataModel]:
        """
        The series description specific query consists in obtaining only the images that have the given series
        descriptions. The final dataset therefore contains both the segmentations and their corresponding images.

        Returns
        -------
        image_data : List[ImageAndSegmentationDataModel]
            image_data
        """
        data = []
        for image_idx, image in enumerate(self._images_data):
            if image.dicom_header.SeriesDescription in self.flatten_series_descriptions:
                image_data = ImageAndSegmentationDataModel(image=image)
                data.append(image_data)

        return data

    def segmentation_and_series_description_specific_query(self) -> List[ImageAndSegmentationDataModel]:
        """
        The segmentation and series description specific query consists of obtaining the images that have the same
        serial uids as those contained in the file names of the given segmentations and the images that have the given
        series descriptions.

        Returns
        -------
        image_and_segmentation_data : List[ImageAndSegmentationDataModel]
            image_and_segmentation_data
        """
        data = []
        for image_idx, image in enumerate(self._images_data):
            image_added = False
            for path_to_segmentation in self.paths_to_segmentation:
                if image.dicom_header.SeriesInstanceUID in path_to_segmentation:
                    segmentation_reader = SegmentationReader(path_to_segmentation=path_to_segmentation)

                    image_and_segmentation_data = ImageAndSegmentationDataModel(
                        image=image,
                        segmentation=segmentation_reader.get_segmentation_data()
                    )
                    data.append(image_and_segmentation_data)
                    image_added = True

            series_description = image.dicom_header.SeriesDescription
            if series_description in self.flatten_series_descriptions and image_added is False:
                image_data = ImageAndSegmentationDataModel(image=image)
                data.append(image_data)

        return data

    def query_functions(self) -> QueryTypeFunction:
        """
        Name of the type of queries associated with their respective function that is used to retrieve the corresponding
        data from the patient's dicom files and from the given segmentations.

        Returns
        -------
        query_functions : QueryTypeFunction
            query_functions
        """
        query_functions = self.QueryTypeFunction(
            DEFAULT=self.default_query,
            SEGMENTATION=self.segmentation_specific_query,
            SERIES_DESCRIPTION=self.series_description_specific_query,
            SEGMENTATION_AND_SERIES_DESCRIPTION=self.segmentation_and_series_description_specific_query
        )

        return query_functions

    @property
    def query_type(self) -> QueryTypeName:
        """
        Get the name of the query type to use based on the value of the variables "path_to_segmentation" and
        "series_descriptions" given to the PatientDataReader class instance.

        Returns
        -------
        query_type_name : QueryTypeName
            query_type_name
        """
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
        """
        Get the query function to use based on the name of the query type.

        Returns
        -------
        query_function : Callable
            query_function
        """
        return getattr(self.query_functions(), self.query_type.name)

    def get_patient_dataset(self) -> PatientDataModel:
        """
        Get the patient dataset.

        Returns
        -------
        patient_dataset : PatientDataModel
            A named tuple grouping the patient's data extracted from its dicom files and the patient's medical image
            segmentation data extracted from the segmentation files.
        """
        patient_dataset = PatientDataModel(
            patient_name=self.patient_name,
            data=self.query_function()
        )

        return patient_dataset
