"""
    @file:              segmentation.py
    @Author:            Maxence Larose

    @Creation Date:     10/2021
    @Last modification: 10/2021

    @Description:       This file contain the class Segmentation that is used to . The
                        goal of this class is to defined the methods that are used to get the total number of segments
                        and get the segment data corresponding to a given segment index.
"""

from typing import Dict, List

import numpy as np

from src.constants.segmentation_category import SegmentationCategory, SegmentationCategories
from src.data_model import SegmentDataModel


class Segmentation:

    def __init__(
            self,
            path_to_segmentation: str,
    ):
        """
        Used for the composition of the different Segmentation classes based on the given segmentation category.

        Parameters
        ----------
        path_to_segmentation : str
            The path to the segmentation file.
        """
        self.path_to_segmentation = path_to_segmentation

    @property
    def segmentation_category(self) -> SegmentationCategory:
        possible_segmentation_categories: List[SegmentationCategory] = []
        for segmentation_category in list(SegmentationCategories):
            if self.path_to_segmentation.endswith(segmentation_category.file_extension):
                possible_segmentation_categories.append(segmentation_category)

        return max(possible_segmentation_categories, key=len)

    @property
    def _loading_class_instance(self):
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
