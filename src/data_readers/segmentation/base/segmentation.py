"""
    @file:              segmentation.py
    @Author:            Maxence Larose

    @Creation Date:     12/2021
    @Last modification: 12/2021

    @Description:       This file contains the class Segmentation.
"""

from typing import Dict, List

import numpy as np

from .segment import Segment


class Segmentation:
    """
    A class used as a reference for all other abstract segmentation classes. These classes will differ by the extension
    of the segmentation files they are able to read.
    """

    def __init__(self, segments: List[Segment]):
        """
        Constructor of the segmentation object.

        Parameters
        ----------
        segments : List[Segment]
            List of all the segments.
        """
        self._segments = segments

    def __len__(self) -> int:
        """
        Number of segments in the segmentation.

        Returns
        -------
        number_of_segments : int
            Number of segments
        """
        return len(self._segments)

    def __getitem__(self, index: int) -> Segment:
        """
        Get a specific segment using its index.

        Parameters
        ----------
        index : int
            Segment index. The possible values of the segment index are [0, 1, ..., self.number_of_segments].

        Returns
        -------
        segment_data : SegmentDataModel
            The segment data.
        """
        return self._segments[index]

    def __setitem__(self, index: int, value) -> None:
        """
        Set a segment using its index and its value.

        Parameters
        ----------
        index : int
            Segment index. The possible values of the segment index are [0, 1, ..., self.number_of_segments].

        Returns
        -------
        segment_data : SegmentDataModel
            The segment data.
        """
        self._segments[index] = value

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
        return {segment.name: segment.label_map for segment in self._segments}
