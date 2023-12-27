"""
    @file:              patient_data_factories.py
    @Author:            Maxence Larose

    @Creation Date:     01/2022
    @Last modification: 03/2022

    @Description:       This file contains all factories that inherit from the BasePatientDataFactory class.
"""

from typing import Dict, List, Optional, Tuple, Union

from delia.readers.patient_data.factories.base_patient_data_factory import BasePatientDataFactory
from delia.readers.image.dicom_reader import DicomReader
from delia.readers.segmentation.segmentation_reader import SegmentationReader
from delia.utils.data_model import ImageAndSegmentationDataModel, PatientDataModel


class DefaultPatientDataFactory(BasePatientDataFactory):
    """
    Class that defines the methods that are used to get the patient data. The default factory consists in obtaining all
    the images.
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
        Constructor of the class DefaultPatientDataFactory.

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
            A set of the organs to segment.
        erase_unused_dicom_files: bool = False
            Whether to delete unused DICOM files or not. Use with caution.
        """
        super().__init__(
            path_to_patient_folder=path_to_patient_folder,
            paths_to_segmentations=paths_to_segmentations,
            tag_values=tag_values,
            tag=tag,
            organs=organs,
            erase_unused_dicom_files=erase_unused_dicom_files
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
        for image_idx, image in enumerate(self._images_data):
            segmentations = []
            for path_to_segmentation in self._paths_to_segmentations:
                seg_header = DicomReader.get_dicom_header(path_to_dicom=path_to_segmentation)
                reference_uid = self.get_segmentation_reference_uid(seg_header)

                if image.dicom_header.SeriesInstanceUID == reference_uid:
                    segmentation_reader = SegmentationReader(
                        image=image,
                        path_to_segmentation=path_to_segmentation,
                        organs=self._organs
                    )

                    segmentations.append(segmentation_reader.get_segmentation_data())

            if segmentations:
                image_and_segmentation_data = ImageAndSegmentationDataModel(
                    image=image,
                    segmentations=segmentations
                )
                data.append(image_and_segmentation_data)
            else:
                image_data = ImageAndSegmentationDataModel(image=image)
                data.append(image_data)

        patient_data = PatientDataModel(
            patient_id=self.patient_id,
            patient_path=self.patient_path,
            data=data
        )
        return patient_data


class SpecificTagPatientDataFactory(BasePatientDataFactory):
    """
    Class that defines the methods that are used to get the patient data. The tag value patient data factory
    consists in obtaining only the images that have the given tag's desired value and their corresponding segmentations.
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
        Constructor of the class SpecificTagPatientDataFactory.

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
            A set of the organs to segment.
        erase_unused_dicom_files: bool = False
            Whether to delete unused DICOM files or not. Use with caution.
        """
        super().__init__(
            path_to_patient_folder=path_to_patient_folder,
            paths_to_segmentations=paths_to_segmentations,
            tag_values=tag_values,
            tag=tag,
            organs=organs,
            erase_unused_dicom_files=erase_unused_dicom_files
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
        for image_idx, image in enumerate(self._images_data):
            image_added = False
            if isinstance(image.dicom_header[self.tag].value, str):
                tag_value = image.dicom_header[self.tag].value
            else:
                tag_value = image.dicom_header[self.tag].repval
            for series_key, list_of_tag_values in self._tag_values.items():
                if tag_value in list_of_tag_values:
                    image.series_key = series_key

                    segmentations = []
                    for path_to_segmentation in self._paths_to_segmentations:
                        seg_header = DicomReader.get_dicom_header(path_to_dicom=path_to_segmentation)
                        reference_uid = self.get_segmentation_reference_uid(seg_header)

                        if image.dicom_header.SeriesInstanceUID == reference_uid:
                            segmentation_reader = SegmentationReader(
                                image=image,
                                path_to_segmentation=path_to_segmentation,
                                organs=self._organs
                            )

                            segmentations.append(segmentation_reader.get_segmentation_data())

                    if segmentations:
                        image_and_segmentation_data = ImageAndSegmentationDataModel(
                            image=image,
                            segmentations=segmentations
                        )
                        data.append(image_and_segmentation_data)
                    else:
                        image_data = ImageAndSegmentationDataModel(image=image)
                        data.append(image_data)

                    image_added = True
                    break

            if image_added is False and self._erase_unused_dicom_files:
                self.erase_dicom_files(image)

        patient_data = PatientDataModel(
            patient_id=self.patient_id,
            patient_path=self.patient_path,
            data=data
        )
        return patient_data
