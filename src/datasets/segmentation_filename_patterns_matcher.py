import os
import re
import logging
from copy import deepcopy
from typing import List

import SimpleITK as sitk
import numpy as np

from src.constants.segmentation_category import SegmentationCategory
from src.data_readers.segmentation.segmentation import Segmentation
from src.data_model import SegmentationDataModel


class SegmentationFilenamePatternsMatcher:

    def __init__(
            self,
            path_to_segmentations_folder: str,
            patient_name: str,
    ):
        """
        Used to load a segmentation file (.nrrd) and obtain data from this file.

        Parameters
        ----------
        path_to_segmentations_folder : str
            Path to the folder containing all segmentations.
        patient_name : str
            Patient name. Must contains the patient number.
        segmentation_category : SegmentationCategory
            Segmentation category.

        Attributes
        ----------
        self.patient_number: int
            Patient number.
        """
        self.path_to_segmentations_folder = path_to_segmentations_folder
        self.patient_name = patient_name

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
        Set patient name and patient number accordingly.

        Parameters
        ----------
        patient_name : str
            Patient name. Must contains the patient number.
        """
        assert any(char.isdigit() for char in patient_name), "Patient names must contain a number."

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
        Pattern in the file name related to the selected segmentation's category.

        Returns
        -------
        pattern : str
            Pattern.
        """
        return [f"Ano{str(self.patient_number)}"]

    @property
    def matches(self) -> List[bool]:
        matches = [False] * len(os.listdir(self.path_to_segmentations_folder))

        for path_idx, path_to_segmentation_file in enumerate(os.listdir(self.path_to_segmentations_folder)):
            if all(pattern in path_to_segmentation_file for pattern in self.patterns):
                matches[path_idx] = True

        return matches

    def get_absolute_path_to_segmentation_file(
            self,
    ) -> List[str]:
        """
        Get segmentation data from the path of the folder containing all patient segmentations, from the patient name
        and from the image modality. The number contained in the given patient name is used to locate the segmentation
        file associated to this patient in the folder.

        WARNING : The segmentation filename must contains the patient number.

        Returns
        -------
        segmentation : List[str]
            A named tuple grouping the segmentation as several binary label maps (one for each organ in the
            segmentation), the segmentation as a simpleITK image, and finally, metadata about the organs/segments that
            are found in the segmentation.
        """
        path_to_segmentations_files = os.listdir(self.path_to_segmentations_folder)
        paths_to_segmentation_file = [path_to_segmentations_files[i] for i in np.where(self.matches)[0]]

        absolute_paths_to_segmentation = []
        for path_to_segmentations_file in paths_to_segmentation_file:
            absolute_path_to_segmentation = os.path.join(self.path_to_segmentations_folder, path_to_segmentations_file)
            absolute_paths_to_segmentation.append(absolute_path_to_segmentation)

        # logging.warning(f"No segmentation found in given segmentation folder {self.path_to_segmentations_folder} "
        #                 f"for patient {self.patient_name} and modality {modality}. If this is unexpected, make "
        #                 f"sure that the segmentation filename contains the patient number.")

        return absolute_paths_to_segmentation
