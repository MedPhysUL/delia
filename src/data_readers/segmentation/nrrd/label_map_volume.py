"""
    @file:              label_map_volume.py
    @Author:            Maxence Larose

    @Creation Date:     10/2021
    @Last modification: 10/2021

    @Description:       This file contain the class LabelMapVolume that inherit from the BaseNrrdSegmentation class. The
                        goal of this class is to defined the methods that are used to get the total number of segments
                        and get the segment data corresponding to a given segment index.
"""

import numpy as np

from src.data_model import SegmentDataModel
from src.data_readers.segmentation.base.base_nrrd_segmentation import BaseNrrdSegmentation


class LabelMapVolume(BaseNrrdSegmentation):

    def __init__(
            self,
            path_to_segmentation: str
    ):
        """
        Used to load the segmentation data from the path to segmentation.

        Parameters
        ----------
        path_to_segmentation : str
            The path to the segmentation file.

        Attributes
        ----------
        self._segmentation_data : Tuple[np.ndarray, OrderedDict]
            Tuple containing the segmentation array and header.
        """
        super(LabelMapVolume, self).__init__(
            path_to_segmentation=path_to_segmentation
        )

    @property
    def number_of_segments(self) -> int:
        """
        Number of segments in the segmentation.

        Returns
        -------
        number_of_segments : int
            Number of segments
        """
        return int(len(np.unique(self.segmentation_array)) - 1)

    def _get_segment_from_segment_idx(self, segment_idx: int) -> SegmentDataModel:
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
        segment = SegmentDataModel(
            name=f"Segment_{segment_idx + 1}",
            layer=0,
            label_value=segment_idx + 1
        )

        return segment
