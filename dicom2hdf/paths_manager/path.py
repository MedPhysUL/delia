"""
    @file:              path.py
    @Author:            Maxence Larose

    @Creation Date:     01/2022
    @Last modification: 01/2022

    @Description:       This file contains the Path class.
"""

from typing import Optional, List

from ..data_readers.patient_data.patient_data_reader import PatientDataReader
from .segmentation_filename_patterns_matcher import SegmentationFilenamePatternsMatcher


class Path:
    """
    A class to represent a Path object.
    """

    def __init__(
            self,
            path_to_dicom_folder: str,
            path_to_segmentations_folder: str,
            verbose: bool,
            patient_number_prefix: str,
    ):
        """
        Used to initialize all the attributes.

        Parameters
        ----------
        path_to_dicom_folder : str
            Path to the folder containing the patient dicom files.
        path_to_segmentations_folder : str
            Path to the folder containing the segmentation files.
        verbose : bool
            True to log/print some information else False.
        patient_number_prefix : str
            The patient number prefix used in the filename of all segmentations.
        """
        self._path_to_dicom_folder = path_to_dicom_folder
        self._path_to_segmentations_folder = path_to_segmentations_folder
        self._patient_number_prefix = patient_number_prefix
        self._verbose = verbose
        self._set_paths_to_segmentations()

    @property
    def path_to_dicom_folder(self) -> str:
        """
        Path to dicom folder property.

        Returns
        -------
        path_to_dicom_folder : str
            Path to the folder containing the patient dicom files.
        """
        return self._path_to_dicom_folder

    @property
    def paths_to_segmentations(self) -> Optional[List[str]]:
        """
        Paths to segmentations.

        Returns
        -------
        path_to_segmentations : Optional[List[str]]
            A list of paths to the segmentation files. The name of the segmentation files must include the series uid of
            their corresponding image, i.e. the image on which the segmentation was made.
        """
        return self._paths_to_segmentations

    def _set_paths_to_segmentations(self):
        """
        Set paths to segmentations.
        """
        patient_data_reader = PatientDataReader(
            path_to_dicom_folder=self._path_to_dicom_folder,
            verbose=True,
        )

        segmentation_filename_patterns_matcher = SegmentationFilenamePatternsMatcher(
            path_to_segmentations_folder=self._path_to_segmentations_folder,
            patient_name=patient_data_reader.patient_name,
            patient_number_prefix=self._patient_number_prefix
        )

        self._paths_to_segmentations = segmentation_filename_patterns_matcher.get_absolute_paths_to_segmentation_files()
