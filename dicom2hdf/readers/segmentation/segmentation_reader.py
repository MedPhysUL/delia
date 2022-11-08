"""
    @file:              segmentation_reader.py
    @Author:            Maxence Larose

    @Creation Date:     10/2021
    @Last modification: 01/2022

    @Description:       This file contains the SegmentationReader class which is used to read a given segmentation file
                        and transform its contents into the format of the SegmentationDataModel class.
"""

from .segmentation_context import SegmentationContext
from .factories.segmentation import Segmentation
from ...utils.data_model import ImageDataModel, SegmentationDataModel


class SegmentationReader:
    """
    A class used to read a given segmentation file and transform its contents into the standard format of the
    SegmentationDataModel class.
    """

    def __init__(
            self,
            image: ImageDataModel,
            path_to_segmentation: str,
    ):
        """
        Constructor of the class SegmentationReader.

        Parameters
        ----------
        image : ImageDataModel
            A named tuple grouping the patient's dicom header, its medical image as a simpleITK image and a sequence of
            the paths to each dicom contained in the series.
        path_to_segmentation : str
            The path to the segmentation file.
        """
        self._image = image
        self._path_to_segmentation = path_to_segmentation

    @property
    def __segmentation_context_manager(self) -> SegmentationContext:
        """
        Creates a SegmentationContext object.

        Returns
        -------
        segmentation_context : SegmentationContext
            Segmentation context manager.
        """
        return SegmentationContext(
            image=self._image,
            path_to_segmentation=self._path_to_segmentation
        )

    @property
    def __segmentation(self) -> Segmentation:
        """
        Creates a Segmentation object.

        Returns
        -------
        segmentation : Segmentation
            Segmentation.
        """
        return self.__segmentation_context_manager.create_segmentation()

    def get_segmentation_data(self) -> SegmentationDataModel:
        """
        Get the segmentation data from the path of the segmentation file.

        Returns
        -------
        segmentation_data : SegmentationDataModel
            A named tuple grouping the segmentation data.
        """
        segmentation_data = SegmentationDataModel(
            modality=self.__segmentation_context_manager.segmentation_strategy.modality,
            simple_itk_label_maps=self.__segmentation.simple_itk_label_maps
        )

        return segmentation_data
