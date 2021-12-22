"""
    @file:              base_nrrd_segmentation_builder.py
    @Author:            Maxence Larose

    @Creation Date:     10/2021
    @Last modification: 12/2021

    @Description:       This file contains the abstract class BaseNrrdSegmentationBuilder that inherit from the
                        SegmentationBuilder class.
"""

from abc import abstractmethod
from collections import OrderedDict
from typing import Dict, List, NamedTuple, Tuple

import nrrd
import numpy as np

from src.constants.organ import Organs
from src.data_readers.segmentation.base.segment import Segment
from src.data_readers.segmentation.base.segmentation_builder import SegmentationBuilder


class SegmentData(NamedTuple):
    """
    A named tuple grouping all the important information of a specific segment in the nrrd segmentation.

    Elements
    --------
    name : str
        The segment name.
    layer : int
        The layer of the segment in the 4D mask array.
    label_value : int
        The label value of the segment in the 3D mask array.
    """
    name: str = None
    layer: int = None
    label_value: int = None


class BaseNrrdSegmentationBuilder(SegmentationBuilder):
    """
    An abstract class used as a reference for all other segmentation classes that read data from files with a ".nrrd"
    extension. These classes differ by the type of segmentation they are able to read. Indeed, the format of the
    segmentations may be different even if the file extension is the same, because there is multiple ways of
    representing a segment.
    """

    def __init__(
            self,
            path_to_segmentation: str,
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
        super(SegmentationBuilder, self).__init__()

        self._segmentation_data: Tuple[np.ndarray, OrderedDict] = nrrd.read(filename=path_to_segmentation)

    @property
    @abstractmethod
    def number_of_segments(self) -> int:
        """
        Number of segments in the segmentation.

        Returns
        -------
        number_of_segments : int
            Number of segments
        """
        pass

    @abstractmethod
    def _get_segment_from_segment_idx(self, segment_idx: int) -> SegmentData:
        """
        Get the segment data by using its index in the segment list found in the segmentation file.

        Parameters
        ----------
        segment_idx : int
            Segment index. The possible values of the segment index are [0, 1, ..., self.number_of_segments].

        Returns
        -------
        segment_data : SegmentData
            The segment data.
        """
        pass

    @property
    def segmentation_array(self) -> np.ndarray:
        """
        Segmentation array.

        Returns
        -------
        segmentation_array : np.ndarray
            Segmentation as a 3D or 4D array.
        """
        return self._segmentation_data[0]

    @property
    def _segmentation_header(self) -> OrderedDict:
        """
        Segmentation header.

        Returns
        -------
        segmentation_header : OrderedDict
            SimpleITK segmentation header.
        """
        return self._segmentation_data[1]

    @property
    def _segments_data(self) -> List[SegmentData]:
        """
        List of all the segments data in the segmentation.

        Returns
        -------
        _segments : List[SegmentData]
            List of all the segments data in the segmentation.
        """
        segments = []
        for segment_idx in range(self.number_of_segments):
            segment = self._get_segment_from_segment_idx(segment_idx=segment_idx)
            segments.append(segment)

        return segments

    @property
    def _segments_names(self) -> List[str]:
        """
        List of all the segment names.

        Returns
        -------
        _segments_names : List[str]
            List of all the segment names.
        """
        segments_names = [segment_data.name for segment_data in self._segments_data]

        return segments_names

    @property
    def _segments_names_associated_to_their_respective_organ(self) -> Dict[str, str]:
        """
        A dictionary of all the segment names associated to their respective organ.

        Returns
        -------
        segments_names_associated_to_their_respective_organ : Dict[str, str]
            A dictionary of all the segment names associated to their respective organ. Keys are segment names and
            values are organ names.
        """
        segment_names_associated_to_their_respective_organ = {}
        for segment_name in self._segments_names:
            for organ in Organs:
                if segment_name in organ.segment_names:
                    segment_names_associated_to_their_respective_organ[segment_name] = organ.name
            if segment_name not in segment_names_associated_to_their_respective_organ:
                raise ValueError(f"Segment name {segment_name} doesn't correspond to any organ in the {Organs} class, "
                                 f"which are {[organ.name for organ in Organs]}")

        return segment_names_associated_to_their_respective_organ

    def _get_the_label_map_of_a_specific_segment(self, segment: SegmentData) -> np.ndarray:
        """
        Get the binary label map associated to a given segment.

        Parameters
        ----------
        segment : SegmentData
            Segment data.

        Returns
        -------
        label_map : np.ndarray
            Binary label map of a specific segment.
        """
        if self.segmentation_array.ndim == 3:
            array = self.segmentation_array
        elif self.segmentation_array.ndim == 4:
            array = self.segmentation_array[segment.layer]
        else:
            raise ValueError(f"Segmentation array must be of dimension 3 or 4. Given array is of dimension "
                             f"{self.segmentation_array.ndim}.")

        label_map = np.zeros_like(array)
        segment_values_idx = np.where(array == segment.label_value)
        label_map[segment_values_idx] = 1

        return label_map

    @property
    def segments(self) -> List[Segment]:
        """
        Segments property.

        Returns
        -------
        segments : List[Segment]
            List of all the segments.
        """
        segments = []
        for segment in self._segments_data:
            organ_name = self._segments_names_associated_to_their_respective_organ[segment.name]
            label_map = self._get_the_label_map_of_a_specific_segment(segment=segment)

            segments.append(Segment(name=organ_name, label_map=label_map))

        return segments
