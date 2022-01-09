"""
    @file:              segmentation_label_map_representation_factory.py
    @Author:            Maxence Larose

    @Creation Date:     10/2021
    @Last modification: 01/2022

    @Description:       This file contains the class SegmentationLabelMapRepresentationFactory that inherit from the
                        BaseNrrdSegmentationFactory class. The goal of this class is to defined the methods that are
                        used to get the total number of segments and get the segment data corresponding to a given
                        segment index.
"""

import re
from typing import Dict, List

import numpy as np

from src.data_readers.segmentation.base.nrrd_segmentation_factory import BaseNrrdSegmentationFactory, SegmentData


class SegmentationLabelMapRepresentationFactory(BaseNrrdSegmentationFactory):
    """
    Class that defined the methods that are used to get the total number of segments and get the segment data
    corresponding to a given segment index for the segmentation label map representation type of segmentation.
    """

    def __init__(
            self,
            path_to_segmentation: str,
            organs: Dict[str, List[str]]
    ):
        """
        Used to load the segmentation data from the path to segmentation.

        Parameters
        ----------
        path_to_segmentation : str
            The path to the segmentation file.
        organs : Dict[str, List[str]]
            A dictionary that contains the organs and their associated segment names. Keys are arbitrary organ names
            and values are lists of possible segment names.

        Attributes
        ----------
        self._segmentation_data : Tuple[np.ndarray, OrderedDict]
            Tuple containing the segmentation array and header.
        """
        super(SegmentationLabelMapRepresentationFactory, self).__init__(
            path_to_segmentation=path_to_segmentation,
            organs=organs
        )

    @property
    def number_of_segments(self) -> int:
        """
        Number of segments in the segmentation.

        Returns
        -------
        _number_of_segments : int
            Number of segments
        """
        r = re.compile(r"Segment\d+_ID")
        return int(np.sum([1 if r.match(key) else 0 for key in list(self._segmentation_header.keys())]))

    def _get_segment_from_segment_idx(self, segment_idx: int) -> SegmentData:
        """
        Get the segment data by using its index in the segment list found in the segmentation metadata.

        Parameters
        ----------
        segment_idx : int
            Segment index. The possible values of the segment index are [0, 1, ..., self.number_of_segments].

        Returns
        -------
        segment_data : SegmentDataModel
            The segment data.
        """
        segment = SegmentData(
            name=self._segmentation_header[f"Segment{segment_idx}_Name"],
            layer=int(self._segmentation_header[f"Segment{segment_idx}_Layer"]),
            label_value=int(self._segmentation_header[f"Segment{segment_idx}_LabelValue"])
        )

        return segment
