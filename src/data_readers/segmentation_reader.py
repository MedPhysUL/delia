"""
    @file:              segmentation_reader.py
    @Author:            Maxence Larose

    @Creation Date:     10/2021
    @Last modification: 01/2022

    @Description:       This file contains the SegmentationReader class which is used to read a given segmentation file
                        and transform its contents into the format of the SegmentationDataModel class.
"""

import SimpleITK as sitk

from src.data_readers.segmentation.segmentation_context import SegmentationContext
from src.data_readers.segmentation.base.segmentation import Segmentation
from src.data_model import SegmentationDataModel


class SegmentationReader:
    """
    A class used to read a given segmentation file and transform its contents into the standard format of the
    SegmentationDataModel class.
    """

    def __init__(
            self,
            path_to_segmentation: str
    ):
        """
        Constructor of the class SegmentationReader.

        Parameters
        ----------
        path_to_segmentation : str
            The path to the segmentation file.
        """
        self._path_to_segmentation = path_to_segmentation

    @property
    def __simple_itk_label_image(self) -> sitk.Image:
        """
        Simple ITK label map image.

        Returns
        -------
        simple_itk_label_map : sitk.Image
            The segmentation as a SimpleITK image.
        """
        file_reader = sitk.ImageFileReader()
        file_reader.SetFileName(fn=self._path_to_segmentation)
        simple_itk_label_map = file_reader.Execute()

        return simple_itk_label_map

    @property
    def __segmentation(self) -> Segmentation:
        """
        Creates a Segmentation object.

        Returns
        -------
        segmentation : Segmentation
            Segmentation.
        """
        segmentation_context_manager = SegmentationContext(path_to_segmentation=self._path_to_segmentation)

        return segmentation_context_manager.create_segmentation()

    def get_segmentation_data(self) -> SegmentationDataModel:
        """
        Get the segmentation data from the path of the segmentation file.

        Returns
        -------
        segmentation_data : SegmentationDataModel
            A named tuple grouping the segmentation as several binary label maps (one for each organ in the
            segmentation), the segmentation as a simpleITK image, and finally, metadata about the organs/segments that
            are found in the segmentation.
        """
        segmentation_data = SegmentationDataModel(
            binary_label_maps=self.__segmentation.label_maps,
            simple_itk_label_map=self.__simple_itk_label_image
        )

        return segmentation_data
