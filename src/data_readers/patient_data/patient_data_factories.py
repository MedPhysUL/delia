"""
    @file:              patient_data_factories.py
    @Author:            Maxence Larose

    @Creation Date:     01/2022
    @Last modification: 01/2022

    @Description:       This file contains all factories that inherit from the BasePatientDataFactory class.
"""

from typing import Dict, List, Optional

from src.data_model import ImageDataModel, ImageAndSegmentationDataModel, PatientDataModel
from src.data_readers.patient_data.base_patient_data_factory import BasePatientDataFactory
from src.data_readers.segmentation_reader import SegmentationReader


class DefaultPatientDataFactory(BasePatientDataFactory):
    """
    Class that defined the methods that are used to get the patient data. The default factory consists in obtaining all
    the images without any segmentation.
    """

    def __init__(
            self,
            images_data: List[ImageDataModel],
            organs: Dict[str, List[str]],
            paths_to_segmentations: Optional[List[str]] = None,
            series_descriptions: Optional[Dict[str, List[str]]] = None
    ):
        """
        Constructor of the class BasePatientDataFactory.

        Parameters
        ----------
        images_data : List[ImageDataModel]
            A list of the patient's images data.
        organs : Dict[str, List[str]]
            A dictionary that contains the organs and their associated segment names. Keys are arbitrary organ names
            and values are lists of possible segment names.
        paths_to_segmentations : Optional[List[str]]
            A list of paths to the segmentation files. The name of the segmentation files must include the series uid
            of their corresponding image, i.e. the image on which the segmentation was made.
        series_descriptions : Optional[Dict[str, List[str]]]
            A dictionary that contains the series descriptions of the images that absolutely needs to be extracted from
            the patient's file. Keys are arbitrary names given to the images we want to add and values are lists of
            series descriptions. The images associated with these series descriptions do not need to have a
            corresponding segmentation. In fact, the whole point of adding a way to specify the series descriptions that
            must be added to the dataset is to be able to add images without segmentation.
        """
        super(DefaultPatientDataFactory, self).__init__(
            images_data=images_data,
            organs=organs,
            paths_to_segmentations=paths_to_segmentations,
            series_descriptions=series_descriptions
        )

    def create_patient_data(self) -> PatientDataModel:
        """
        Creates a tuple containing all the patient's data.

        Returns
        -------
        patient_data: PatientDataModel
            Patient data.
        """
        patient_data = PatientDataModel(
            patient_name=self.patient_name,
            data=[ImageAndSegmentationDataModel(image=image) for image in self._images_data]
        )
        return patient_data


class SegmentationPatientDataFactory(BasePatientDataFactory):
    """
    Class that defined the methods that are used to get the patient data. The segmentation patient data factory consists
    in obtaining the images that have the same serial uids as those contained in the file names of the given
    segmentations. The final dataset therefore contains both the segmentations and their corresponding images.
    """

    def __init__(
            self,
            images_data: List[ImageDataModel],
            organs: Dict[str, List[str]],
            paths_to_segmentations: Optional[List[str]] = None,
            series_descriptions: Optional[Dict[str, List[str]]] = None
    ):
        """
        Constructor of the class SegmentationOnlyPatientDataFactory.

        Parameters
        ----------
        images_data : List[ImageDataModel]
            A list of the patient's images data.
        organs : Dict[str, List[str]]
            A dictionary that contains the organs and their associated segment names. Keys are arbitrary organ names
            and values are the list of possible segment names for each organ.
        paths_to_segmentations : Optional[List[str]]
            A list of paths to the segmentation files. The name of the segmentation files must include the series uid
            of their corresponding image, i.e. the image on which the segmentation was made.
        series_descriptions : Optional[Dict[str, List[str]]]
            A dictionary that contains the series descriptions of the images that absolutely needs to be extracted from
            the patient's file. Keys are arbitrary names given to the images we want to add and values are lists of
            series descriptions. The images associated with these series descriptions do not need to have a
            corresponding segmentation. In fact, the whole point of adding a way to specify the series descriptions that
            must be added to the dataset is to be able to add images without segmentation.
        """
        super(SegmentationPatientDataFactory, self).__init__(
            images_data=images_data,
            organs=organs,
            paths_to_segmentations=paths_to_segmentations,
            series_descriptions=series_descriptions
        )

    def create_patient_data(self) -> PatientDataModel:
        """
        Creates a tuple containing all the patient's data.

        Returns
        -------
        patient_data: PatientDataModel
            Patient data.
        """
        data = []
        for image in self._images_data:
            for path_to_segmentation in self._paths_to_segmentations:
                if image.dicom_header.SeriesInstanceUID in path_to_segmentation:
                    segmentation_reader = SegmentationReader(path_to_segmentation=path_to_segmentation)

                    image_and_segmentation_data = ImageAndSegmentationDataModel(
                        image=image,
                        segmentation=segmentation_reader.get_segmentation_data()
                    )

                    data.append(image_and_segmentation_data)

        patient_data = PatientDataModel(
            patient_name=self.patient_name,
            data=data
        )
        return patient_data


class SeriesDescriptionPatientDataFactory(BasePatientDataFactory):
    """
    Class that defined the methods that are used to get the patient data. The series description patient data factory
    consists in obtaining only the images that have the given series descriptions. The final dataset therefore contains
    both the segmentations and their corresponding images.
    """

    def __init__(
            self,
            images_data: List[ImageDataModel],
            organs: Dict[str, List[str]],
            paths_to_segmentations: Optional[List[str]] = None,
            series_descriptions: Optional[Dict[str, List[str]]] = None
    ):
        """
        Constructor of the class SegmentationOnlyPatientDataFactory.

        Parameters
        ----------
        images_data : List[ImageDataModel]
            A list of the patient's images data.
        organs : Dict[str, List[str]]
            A dictionary that contains the organs and their associated segment names. Keys are arbitrary organ names
            and values are the list of possible segment names for each organ.
        paths_to_segmentations : Optional[List[str]]
            A list of paths to the segmentation files. The name of the segmentation files must include the series uid
            of their corresponding image, i.e. the image on which the segmentation was made.
        series_descriptions : Optional[Dict[str, List[str]]]
            A dictionary that contains the series descriptions of the images that absolutely needs to be extracted from
            the patient's file. Keys are arbitrary names given to the images we want to add and values are lists of
            series descriptions. The images associated with these series descriptions do not need to have a
            corresponding segmentation. In fact, the whole point of adding a way to specify the series descriptions that
            must be added to the dataset is to be able to add images without segmentation.
        """
        super(SeriesDescriptionPatientDataFactory, self).__init__(
            images_data=images_data,
            organs=organs,
            paths_to_segmentations=paths_to_segmentations,
            series_descriptions=series_descriptions
        )
        
    @property
    def flatten_series_descriptions(self) -> List[str]:
        """
        Flatten series descriptions.

        Returns
        -------
        flatten_series_description : List[str]
            Series descriptions as a list instead of a dictionary.
        """
        return [val for lst in self._series_descriptions.values() for val in lst]

    def create_patient_data(self) -> PatientDataModel:
        """
        Creates a tuple containing all the patient's data.

        Returns
        -------
        patient_data: PatientDataModel
            Patient data.
        """
        data = []
        for image_idx, image in enumerate(self._images_data):
            if image.dicom_header.SeriesDescription in self.flatten_series_descriptions:
                image_data = ImageAndSegmentationDataModel(image=image)
                data.append(image_data)

        patient_data = PatientDataModel(
            patient_name=self.patient_name,
            data=data
        )
        return patient_data


class SegmentationAndSeriesDescriptionPatientDataFactory(BasePatientDataFactory):
    """
    Class that defined the methods that are used to get the patient data. The segmentation and series description
    factory consists in obtaining the images that have the same serial uids as those contained in the file names of the
    given segmentations and the images that have the given series descriptions.
    """

    def __init__(
            self,
            images_data: List[ImageDataModel],
            organs: Dict[str, List[str]],
            paths_to_segmentations: Optional[List[str]] = None,
            series_descriptions: Optional[Dict[str, List[str]]] = None
    ):
        """
        Constructor of the class SegmentationOnlyPatientDataFactory.

        Parameters
        ----------
        images_data : List[ImageDataModel]
            A list of the patient's images data.
        organs : Dict[str, List[str]]
            A dictionary that contains the organs and their associated segment names. Keys are arbitrary organ names
            and values are the list of possible segment names for each organ.
        paths_to_segmentations : Optional[List[str]]
            A list of paths to the segmentation files. The name of the segmentation files must include the series uid
            of their corresponding image, i.e. the image on which the segmentation was made.
        series_descriptions : Optional[Dict[str, List[str]]]
            A dictionary that contains the series descriptions of the images that absolutely needs to be extracted from
            the patient's file. Keys are arbitrary names given to the images we want to add and values are lists of
            series descriptions. The images associated with these series descriptions do not need to have a
            corresponding segmentation. In fact, the whole point of adding a way to specify the series descriptions that
            must be added to the dataset is to be able to add images without segmentation.
        """
        super(SegmentationAndSeriesDescriptionPatientDataFactory, self).__init__(
            images_data=images_data,
            organs=organs,
            paths_to_segmentations=paths_to_segmentations,
            series_descriptions=series_descriptions
        )

    @property
    def flatten_series_descriptions(self) -> List[str]:
        """
        Flatten series descriptions.

        Returns
        -------
        flatten_series_description : List[str]
            Series descriptions as a list instead of a dictionary.
        """
        return [val for lst in self._series_descriptions.values() for val in lst]
        
    def create_patient_data(self) -> PatientDataModel:
        """
        Creates a tuple containing all the patient's data.

        Returns
        -------
        patient_data: PatientDataModel
            Patient data.
        """
        data = []
        for image_idx, image in enumerate(self._images_data):
            image_added = False
            for path_to_segmentation in self._paths_to_segmentations:
                if image.dicom_header.SeriesInstanceUID in path_to_segmentation:
                    segmentation_reader = SegmentationReader(
                        path_to_segmentation=path_to_segmentation,
                        organs=self._organs
                    )

                    image_and_segmentation_data = ImageAndSegmentationDataModel(
                        image=image,
                        segmentation=segmentation_reader.get_segmentation_data()
                    )
                    data.append(image_and_segmentation_data)
                    image_added = True

            series_description = image.dicom_header.SeriesDescription
            print("SERIES DESCRIPTION", series_description)
            print("FLATTEN SERIES DESCRIPTIONS", self.flatten_series_descriptions)
            print("IMAGE ADDED", image_added)
            if series_description in self.flatten_series_descriptions and image_added is False:
                image_data = ImageAndSegmentationDataModel(image=image)
                data.append(image_data)

        patient_data = PatientDataModel(
            patient_name=self.patient_name,
            data=data
        )
        return patient_data
