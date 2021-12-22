"""
    @file:              segmentation_context_manager.py
    @Author:            Maxence Larose

    @Creation Date:     10/2021
    @Last modification: 12/2021

    @Description:       This file contains the class SegmentationCategoryManager that is used as a context class where
                        states are types of ways to load the segmentation data, or more precisely, types of builders
                        object.
"""

from typing import List

from src.constants.segmentation_category import SegmentationCategory, SegmentationCategories
from src.data_readers.segmentation.base.segmentation import Segmentation


class SegmentationCategoryManager:
    """
    A class used as a context class where states are types of ways to load the segmentation data, or more precisely,
    types of loading segmentation classes. States are entirely defined by the extension of the given file and so, by the
    path of the segmentation.
    """

    def __init__(
            self,
            path_to_segmentation: str,
    ):
        """
        Constructor of the Segmentation class.

        Parameters
        ----------
        path_to_segmentation : str
            The path to the segmentation file.
        """
        self.path_to_segmentation = path_to_segmentation

    @property
    def segmentation_category(self) -> SegmentationCategory:
        """
        Segmentation category corresponding to the given segmentation file extension.

        Returns
        -------
        segmentation_category : SegmentationCategory
            Segmentation category.
        """
        possible_segmentation_categories: List[SegmentationCategory] = []
        for segmentation_category in list(SegmentationCategories):
            if self.path_to_segmentation.endswith(segmentation_category.file_extension):
                possible_segmentation_categories.append(segmentation_category)

        return max(possible_segmentation_categories, key=len)

    @property
    def _builder_instance(self) -> SegmentationCategory.builder:
        """
        The builder class instance corresponding to the class of the given segmentation category.

        Returns
        -------
        _builder_class_instance : SegmentationCategory.builder
            Builder class instance used to get the label maps and the segmentation metadata from a segmentation file.
        """
        return self.segmentation_category.builder(path_to_segmentation=self.path_to_segmentation)

    @property
    def segmentation(self) -> Segmentation:
        """
        Creates a Segmentation object.

        Returns
        -------
        segmentation : Segmentation
            Segmentation.
        """
        return self._builder_instance.make_segmentation()
