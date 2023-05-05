"""
    @file:              segmentation_context.py
    @Author:            Maxence Larose

    @Creation Date:     10/2021
    @Last modification: 01/2022

    @Description:       This file contains the class SegmentationContext that is used as a context class where
                        strategies are types of ways to load the segmentation data, or more precisely, types of
                        segmentation object factory.
"""

import pydicom

from .segmentation_strategy import SegmentationStrategy, SegmentationStrategies
from .factories.segmentation import Segmentation
from ...utils.data_model import ImageDataModel


class SegmentationContext:
    """
    A class used as a context class where strategies are types of ways to load the segmentation data, or more precisely,
    types of segmentation object factory. Strategies are entirely defined by the extension of the given file and so, by
    the path of the segmentation.
    """

    def __init__(
            self,
            image: ImageDataModel,
            path_to_segmentation: str
    ):
        """
        Constructor of the SegmentationContext class.

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
    def path_to_segmentation(self) -> str:
        """
        Path to segmentation property.

        Returns
        -------
        path_to_segmentation : str
            The path to the segmentation file.
        """
        return self._path_to_segmentation

    @path_to_segmentation.setter
    def path_to_segmentation(self, path_to_segmentation: str) -> None:
        """
        Path to segmentation setter.

        Parameters
        ----------
        path_to_segmentation : str
            The path to the segmentation file.
        """
        self._path_to_segmentation = path_to_segmentation

    @property
    def segmentation_modality(self) -> str:
        """
        Segmentation modality.

        Returns
        -------
        segmentation_modality : str
            Segmentation modality.
        """
        modality = self.segmentation_dicom_header.Modality
        available_modalities = SegmentationStrategies.get_available_modalities()

        assert modality in available_modalities, (
            f"The given segmentation file ({self.path_to_segmentation}) is of modality {modality}. However, the "
            f"available modalities for the segmentations are {available_modalities}."
        )

        return modality

    @property
    def segmentation_dicom_header(self) -> pydicom.dataset.FileDataset:
        """
        Segmentation dicom header.

        Returns
        -------
        segmentation_dicom_header : pydicom.dataset.FileDataset
            Segmentation dicom header.
        """
        header = pydicom.dcmread(self.path_to_segmentation, stop_before_pixels=True)

        return header

    @property
    def segmentation_strategy(self) -> SegmentationStrategy:
        """
        Segmentation strategy corresponding to the given segmentation modality.

        Returns
        -------
        segmentation_strategy : SegmentationStrategy
            Segmentation strategy.
        """
        modality = self.segmentation_modality
        for segmentation_category in list(SegmentationStrategies):
            if modality == segmentation_category.value.modality:
                return segmentation_category.value

    @property
    def _segmentation_factory_instance(self) -> SegmentationStrategy.factory:
        """
        The segmentation factory instance corresponding to the class of the given segmentation category.

        Returns
        -------
        _segmentation_factory_instance : SegmentationStrategy.factory
            Factory class instance used to get the label maps and the segmentation metadata from a segmentation file.
        """
        return self.segmentation_strategy.factory(
            image=self._image,
            path_to_segmentation=self.path_to_segmentation
        )

    def create_segmentation(self) -> Segmentation:
        """
        Creates a Segmentation object.

        Returns
        -------
        segmentation : Segmentation
            Segmentation.
        """
        return self._segmentation_factory_instance.create_segmentation()
