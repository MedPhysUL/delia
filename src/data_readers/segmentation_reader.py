import os
import re
from typing import List
import logging

import SimpleITK as sitk
import numpy as np

from src.data_readers.segmentation.segmentation import Segmentation
from src.data_model import SegmentationDataModel


class SegmentationReader:

    def __init__(
            self,
            *args, **kwargs
    ):
        """
        Used to load a segmentation file (.nrrd) and obtain data from this file.
        """
        super(SegmentationReader, self).__init__(*args, **kwargs)

    def get_segmentation_data(
            self,
            path_to_segmentation: str
    ) -> SegmentationDataModel:
        """
        Get segmentation data from the path of the folder containing all patient segmentations, from the patient name
        and from the image modality. The number contained in the given patient name is used to locate the segmentation
        file associated to this patient in the folder.

        WARNING : The segmentation filename must contains the patient number.

        Parameters
        ----------
        modality : str
            Modality.

        Returns
        -------
        segmentation : SegmentationDataModel
            A named tuple grouping the segmentation as several binary label maps (one for each organ in the
            segmentation), the segmentation as a simpleITK image, and finally, metadata about the organs/segments that
            are found in the segmentation.
        """
        file_reader = sitk.ImageFileReader()
        file_reader.SetFileName(fn=path_to_segmentation)
        simple_itk_label_map = file_reader.Execute()

        segmentation = Segmentation(path_to_segmentation=path_to_segmentation)

        segmentation_metadata = segmentation.segmentation_metadata
        binary_label_maps = segmentation.label_maps

        segmentation = SegmentationDataModel(
            binary_label_maps=binary_label_maps,
            simple_itk_label_map=simple_itk_label_map,
            metadata=segmentation_metadata
        )

        return segmentation
