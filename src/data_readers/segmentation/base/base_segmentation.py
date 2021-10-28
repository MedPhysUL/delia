"""
    @file:              base_segmentation.py
    @Author:            Maxence Larose

    @Creation Date:     10/2021
    @Last modification: 10/2021

    @Description:       This file contain the abstract class BaseSegmentation.
"""

from abc import ABC, abstractmethod
from typing import Dict

import numpy as np

from src.data_model import SegmentDataModel


class BaseSegmentation(ABC):
    """
    An abstract class used as a reference for all other abstract segmentation classes. These classes differ by the
    extension of the segmentation files they are able to read.
    """

    @property
    @abstractmethod
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
        pass

    @property
    @abstractmethod
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
        pass
