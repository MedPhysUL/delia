"""
    @file:              base_patient_data_factory.py
    @Author:            Maxence Larose

    @Creation Date:     01/2022
    @Last modification: 03/2022

    @Description:       This file contains the class BasePatientDataFactory that is used as an abstract class used as a
                        reference for all other patient data factories.
"""

from abc import ABC, abstractmethod
from os import remove
from typing import Dict, List, Optional, Tuple, Union

import pydicom

from delia.readers.image.dicom_reader import DicomReader
from delia.utils.data_model import ImageDataModel, PatientDataModel


class BasePatientDataFactory(ABC):
    """
    An abstract class that is used as a reference for all other patient data factories.
    """

    def __init__(
            self,
            path_to_patient_folder: str,
            paths_to_segmentations: Optional[List[str]],
            tag_values: Optional[Dict[str, List[str]]],
            tag: Union[str, Tuple[int, int]],
            organs: Optional[List[str]] = None,
            erase_unused_dicom_files: bool = False
    ):
        """
        Constructor of the class BasePatientDataFactory.

        Parameters
        ----------
        path_to_patient_folder : str
            Path to the folder containing the patient's image files.
        paths_to_segmentations : Optional[List[str]]
            List of paths to the patient's segmentation files.
        tag_values : Optional[Dict[str, List[str]]]
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

        dicom_reader = DicomReader(path_to_patient_folder=self._path_to_patient_folder, tag=self.tag)
        self._images_data = dicom_reader.get_images_data(remove_segmentations=True)

    @property
    def patient_id(self) -> str:
        """
        Patient ID.

        Returns
        -------
        patient_id : str
            Patient ID.
        """
        patient_id = self._images_data[0].dicom_header.PatientID

        return str(patient_id)

    @staticmethod
    def get_segmentation_reference_uid(segmentation_header: pydicom.dataset.FileDataset) -> pydicom.DataElement:
        """
        Get the reference UID of the medical image on which the given segmentation/contouring was performed.

        Parameters
        ----------
        segmentation_header : pydicom.dataset.FileDataset
            Loaded DICOM dataset.

        Returns
        -------
        reference_uid : pydicom.DataElement
            Reference UID of the medical image on which the contouring was performed.
        """
        if hasattr(segmentation_header, "ReferencedSeriesSequence"):
            return segmentation_header.ReferencedSeriesSequence[0].SeriesInstanceUID
        elif hasattr(segmentation_header, "ReferencedFrameOfReferenceSequence"):
            referenced_frame_of_reference_sequence = segmentation_header.ReferencedFrameOfReferenceSequence
            rt_referenced_study_sequence = referenced_frame_of_reference_sequence[0].RTReferencedStudySequence
            rt_referenced_series_sequence = rt_referenced_study_sequence[0].RTReferencedSeriesSequence
            return rt_referenced_series_sequence[0].SeriesInstanceUID
        else:
            raise AssertionError(
                "The segmentation DICOM header must contain either the 'ReferencedSeriesSequence' attribute or "
                "the 'ReferencedFrameOfReferenceSequence' attribute to associate the segmentation with the "
                "corresponding medical image."
            )

    @staticmethod
    def erase_dicom_files(image: ImageDataModel):
        """
        Erases the dicom files associated to a given image.

        Parameters
        ----------
        image : ImageDataModel
            A named tuple grouping the patient's dicom header, its medical image as a simpleITK image and a sequence of
            the paths to each dicom contained in the series.
        """
        for path in image.paths_to_dicoms:
            remove(path)

    @abstractmethod
    def create_patient_data(self) -> PatientDataModel:
        """
        Creates a tuple containing all the patient's data.

        Returns
        -------
        patient_data: PatientDataModel
            Patient data.
        """
        raise NotImplementedError
