"""
    @file:              segmentation_filename_patterns_matcher.py
    @Author:            Maxence Larose

    @Creation Date:     10/2021
    @Last modification: 10/2021

    @Description:       This file contains the SegmentationFilenamePatternsMatcher class whose main purpose is to obtain
                        a list of absolute paths to the segmentation files given the location of the folder containing
                        all the segmentations, the patient name and the patient number prefix used in the name of
                        segmentations file.
"""

import os
import re
from typing import List

import numpy as np


class SegmentationFilenamePatternsMatcher:
    """
    A class whose main purpose is to obtain a list of absolute paths to the segmentation files given the location of the
    folder containing all the segmentations, the patient name and the patient number prefix used in the name of
    segmentations file.
    """

    def __init__(
            self,
            path_to_segmentations_folder: str,
            patient_name: str,
            patient_number_prefix: str
    ):
        """
        Used to initialize all the class' attributes.

        Parameters
        ----------
        path_to_segmentations_folder : str
            Path to the folder containing all segmentations.
        patient_name : str
            Patient name. Must contains the patient number.
        patient_number_prefix : str
            The patient number prefix used in the filename of all segmentations.
        """
        self.path_to_segmentations_folder = path_to_segmentations_folder
        self.patient_name = patient_name
        self.patient_number_prefix = patient_number_prefix

    @property
    def patient_name(self) -> str:
        """
        Patient name.

        Returns
        -------
        patient_name : str
            Patient name. Must contains the patient number.
        """
        return self._patient_name

    @patient_name.setter
    def patient_name(
            self,
            patient_name: str
    ) -> None:
        """
        Set patient name.

        Parameters
        ----------
        patient_name : str
            Patient name. Must contains the patient number.
        """
        assert any(char.isdigit() for char in patient_name), f"Patient names must contain a number. Given name is " \
                                                             f"{patient_name}."

        self._patient_name = patient_name

    @property
    def patient_number(self) -> int:
        """
        Get patient number from patient name.

        Returns
        -------
        patient_number : int
            Patient number.
        """
        patient_number = int(re.findall(pattern=r"\d+", string=self.patient_name)[-1])

        return patient_number

    @property
    def patterns(self) -> List[str]:
        """
        Pattern in the filename.

        Returns
        -------
        pattern : str
            Pattern.
        """
        return [f"{self.patient_number_prefix}{str(self.patient_number)}"]

    @property
    def paths_to_segmentation_files(self) -> List[str]:
        """
        Paths to segmentation files.

        Returns
        -------
        paths : List[str]
            A list of all the paths to the segmentation files.
        """
        return os.listdir(self.path_to_segmentations_folder)

    @property
    def matches(self) -> List[bool]:
        """
        Get a boolean list indicating whether or not the segmentation filenames match the pattern defined using the
        patient number and the patient number prefix.

        Returns
        -------
        matches : List[bool]
            A list of booleans where the value is True if all the patterns are found in the name of the segmentation
            file and False otherwise. The indexes of the list represents a specific segmentation file (see
            paths_to_segmentation_files).
        """
        matches = [False] * len(self.paths_to_segmentation_files)

        for path_idx, path_to_segmentation_file in enumerate(self.paths_to_segmentation_files):
            if all(pattern in path_to_segmentation_file for pattern in self.patterns):
                matches[path_idx] = True

        return matches

    def get_absolute_paths_to_segmentation_files(
            self,
    ) -> List[str]:
        """
        Get the absolute paths of the segmentation files whose filenames match the pattern of the given patient name.

        Returns
        -------
        absolute_paths_to_segmentation : List[str]
            A list of the absolute paths to all the segmentation files whose filenames match the pattern of the given
            patient name.
        """
        paths_to_segmentation_file = [self.paths_to_segmentation_files[i] for i in np.where(self.matches)[0]]

        absolute_paths_to_segmentation = []
        for path_to_segmentations_file in paths_to_segmentation_file:
            absolute_path_to_segmentation = os.path.join(self.path_to_segmentations_folder, path_to_segmentations_file)
            absolute_paths_to_segmentation.append(absolute_path_to_segmentation)

        return absolute_paths_to_segmentation
