"""
    @file:              patient_data_factories.py
    @Author:            Maxence Larose

    @Creation Date:     01/2022
    @Last modification: 03/2022

    @Description:       This file contains all factories that inherit from the BasePatientDataFactory class.
"""

from typing import Dict, List, Optional

from dicom2hdf.data_readers.patient_data.factories.base_patient_data_factory import BasePatientDataFactory
from dicom2hdf.data_model import ImageAndSegmentationDataModel, PatientDataModel
from dicom2hdf.data_readers.image.dicom_reader import DicomReader
from dicom2hdf.data_readers.segmentation.segmentation_reader import SegmentationReader


class DefaultPatientDataFactory(BasePatientDataFactory):
    """
    Class that defines the methods that are used to get the patient data. The default factory consists in obtaining all
    the images without any segmentation.
    """

    def __init__(
            self,
            path_to_patient_folder: str,
            paths_to_segmentations: Optional[List[str]],
            series_descriptions: Optional[Dict[str, List[str]]]
    ):
        """
        Constructor of the class DefaultPatientDataFactory.

        Parameters
        ----------
        path_to_patient_folder : str
            Path to the folder containing the patient's image files.
        paths_to_segmentations : Optional[List[str]]
            List of paths to the patient's segmentation files.
        series_descriptions : Optional[Dict[str, List[str]]]
            A dictionary that contains the series descriptions of the images that absolutely needs to be extracted from
            the patient's file. Keys are arbitrary names given to the images we want to add and values are lists of
            series descriptions.
        """
        super().__init__(
            path_to_patient_folder=path_to_patient_folder,
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
            patient_id=self.patient_id,
            data=[ImageAndSegmentationDataModel(image=image) for image in self._images_data]
        )
        return patient_data


class SegmentationPatientDataFactory(BasePatientDataFactory):
    """
    Class that defines the methods that are used to get the patient data. The segmentation patient data factory consists
    in obtaining the images that have the same serial uids as those contained in the file names of the given
    segmentations. The final dataset therefore contains both the segmentations and their corresponding images.
    """

    def __init__(
            self,
            path_to_patient_folder: str,
            paths_to_segmentations: List[str],
            series_descriptions: Optional[Dict[str, List[str]]]
    ):
        """
        Constructor of the class SegmentationPatientDataFactory.

        Parameters
        ----------
        path_to_patient_folder : str
            Path to the folder containing the patient's image files.
        paths_to_segmentations : Optional[List[str]]
            List of paths to the patient's segmentation files.
        series_descriptions : Optional[Dict[str, List[str]]]
            A dictionary that contains the series descriptions of the images that absolutely needs to be extracted from
            the patient's file. Keys are arbitrary names given to the images we want to add and values are lists of
            series descriptions.
        """
        super().__init__(
            path_to_patient_folder=path_to_patient_folder,
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
            image_added = False
            for path_to_segmentation in self._paths_to_segmentations:
                dicom_header = DicomReader.get_dicom_header(path_to_dicom=path_to_segmentation)
                if image.dicom_header.SeriesInstanceUID == dicom_header.ReferencedSeriesSequence[0].SeriesInstanceUID:
                    segmentation_reader = SegmentationReader(path_to_segmentation=path_to_segmentation)

                    image_and_segmentation_data = ImageAndSegmentationDataModel(
                        image=image,
                        segmentation=segmentation_reader.get_segmentation_data()
                    )

                    data.append(image_and_segmentation_data)
                    image_added = True

            if image_added is False:
                image_data = ImageAndSegmentationDataModel(image=image)
                data.append(image_data)

        patient_data = PatientDataModel(
            patient_id=self.patient_id,
            data=data
        )
        return patient_data


class SeriesDescriptionPatientDataFactory(BasePatientDataFactory):
    """
    Class that defines the methods that are used to get the patient data. The series description patient data factory
    consists in obtaining only the images that have the given series descriptions. The final dataset therefore contains
    both the segmentations and their corresponding images.
    """

    def __init__(
            self,
            path_to_patient_folder: str,
            paths_to_segmentations: Optional[List[str]],
            series_descriptions: Optional[Dict[str, List[str]]]
    ):
        """
        Constructor of the class SeriesDescriptionPatientDataFactory.

        Parameters
        ----------
        path_to_patient_folder : str
            Path to the folder containing the patient's image files.
        paths_to_segmentations : Optional[List[str]]
            List of paths to the patient's segmentation files.
        series_descriptions : Optional[Dict[str, List[str]]]
            A dictionary that contains the series descriptions of the images that absolutely needs to be extracted from
            the patient's file. Keys are arbitrary names given to the images we want to add and values are lists of
            series descriptions.
        """
        super().__init__(
            path_to_patient_folder=path_to_patient_folder,
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
            patient_id=self.patient_id,
            data=data
        )
        return patient_data


class SegAndSeriesPatientDataFactory(BasePatientDataFactory):
    """
    Class that defines the methods that are used to get the patient data. The segmentation and series description
    factory consists in obtaining the images that have the same serial uids as those contained in the file names of the
    given segmentations and the images that have the given series descriptions.
    """

    def __init__(
            self,
            path_to_patient_folder: str,
            paths_to_segmentations: Optional[List[str]],
            series_descriptions: Optional[Dict[str, List[str]]]
    ):
        """
        Constructor of the class SegAndSeriesPatientDataFactory.

        Parameters
        ----------
        path_to_patient_folder : str
            Path to the folder containing the patient's image files.
        paths_to_segmentations : Optional[List[str]]
            List of paths to the patient's segmentation files.
        series_descriptions : Optional[Dict[str, List[str]]]
            A dictionary that contains the series descriptions of the images that absolutely needs to be extracted from
            the patient's file. Keys are arbitrary names given to the images we want to add and values are lists of
            series descriptions.
        """
        super().__init__(
            path_to_patient_folder=path_to_patient_folder,
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
            series_description = image.dicom_header.SeriesDescription
            if series_description in self.flatten_series_descriptions:
                image_added = False
                for path_to_segmentation in self._paths_to_segmentations:
                    seg_header = DicomReader.get_dicom_header(path_to_dicom=path_to_segmentation)
                    if image.dicom_header.SeriesInstanceUID == seg_header.ReferencedSeriesSequence[0].SeriesInstanceUID:
                        segmentation_reader = SegmentationReader(path_to_segmentation=path_to_segmentation)

                        image_and_segmentation_data = ImageAndSegmentationDataModel(
                            image=image,
                            segmentation=segmentation_reader.get_segmentation_data()
                        )
                        data.append(image_and_segmentation_data)
                        image_added = True

                if image_added is False:
                    image_data = ImageAndSegmentationDataModel(image=image)
                    data.append(image_data)

        patient_data = PatientDataModel(
            patient_id=self.patient_id,
            data=data
        )
        return patient_data
