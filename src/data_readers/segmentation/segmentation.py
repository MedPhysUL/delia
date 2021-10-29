"""
    @file:              segmentation.py
    @Author:            Maxence Larose

    @Creation Date:     10/2021
    @Last modification: 10/2021

    @Description:       This file contains the class Segmentation that is used as a context class where states are types
                        of ways to load the segmentation data, or more precisely, types of loading segmentation classes.
"""

from typing import Dict, List

import numpy as np

from src.constants.segmentation_category import SegmentationCategory, SegmentationCategories
from src.data_model import SegmentDataModel


class Segmentation:
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
    def _loading_class_instance(self) -> SegmentationCategory.loading_class:
        """
        The loading class instance corresponding to the class of the given segmentation category.

        Returns
        -------
        _loading_class_instance : SegmentationCategory.loading_class
            Loading class instance used to get the label maps and the segmentation metadata from a segmentation file.
        """
        return self.segmentation_category.loading_class(path_to_segmentation=self.path_to_segmentation)

    @property
    def label_maps(self) -> Dict[str, np.ndarray]:
        """
        Label maps of all the organs/segments that are found in the segmentation file.

        Returns
        -------
        label_maps : Dict[str, np.ndarray]
            A dictionary that contains the name of the organs and their corresponding binary label map. Keys are organ
            names and values are binary label maps. Thus, the label maps dictionary is formatted as follows :

                label_maps = {
                    organ_name (example: "PROSTATE"): np.ndarray,
                    organ_name (example: "RECTUM"): np.ndarray,
                    ...
                }
        """
        return self._loading_class_instance.label_maps

    @property
    def segmentation_metadata(self) -> Dict[str, SegmentDataModel]:
        """
        Segmentation metadata of all the organs/segments that are found in the segmentation file.

        Returns
        -------
        segmentation_metadata : Dict[str, SegmentDataModel]
            A dictionary that contains organs and their corresponding segmentation metadata. Keys are organ names and
            values are tuples containing important information about the segments in the original segmentation image
            (segments name, segments layer, segments label value, etc.). Thus, the segmentation metadata dictionary is
            formatted as follows :

                metadata = {
                    organ_name (example: "PROSTATE"): (
                        name: str
                        layer: int
                        label_value: int
                    ),
                    organ_name (example: "RECTUM"): (
                        name: str
                        layer: int
                        label_value: int
                    ),
                    ...
                }
        """
        return self._loading_class_instance.segmentation_metadata
