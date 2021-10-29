"""
    @file:              base_nrrd_segmentation.py
    @Author:            Maxence Larose

    @Creation Date:     10/2021
    @Last modification: 10/2021

    @Description:       This file contains the abstract class BaseNrrdSegmentation that inherit from the
                        BaseSegmentation class.
"""

from abc import abstractmethod
from collections import OrderedDict
from typing import Dict, List, Tuple

import nrrd
import numpy as np

from src.constants.organ import Organs
from src.data_model import SegmentDataModel
from src.data_readers.segmentation.base.base_segmentation import BaseSegmentation


class BaseNrrdSegmentation(BaseSegmentation):
    """
    An abstract class used as a reference for all other segmentation classes that read data from files with a ".nrrd"
    extension. These classes differ by the type of segmentation they are able to read. Indeed, the format of the
    segmentations may be different even if the file extension is the same.
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
        super(BaseSegmentation, self).__init__()

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
    def _segmentation_array_dimension(self) -> int:
        """
        Segmentation array dimension.

        Returns
        -------
        dimension: int
            Segmentation array dimension.
        """
        return self.segmentation_array.ndim

    @property
    def _segments(self) -> List[SegmentDataModel]:
        """
        List of all the segments data in the segmentation.

        Returns
        -------
        _segments : List[SegmentDataModel]
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
        segments_names = [segment.name for segment in self._segments]

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

    @property
    def segmentation_metadata(self) -> Dict[str, SegmentDataModel]:
        """
        Get the segment data of all the organs/segments that are found in the segmentation file.

        Returns
        -------
        segmentation_metadata : Dict[str, SegmentDataModel]
            A dictionary grouping organs to their corresponding segment metadata. The keys are organ names and the values
            are tuples containing important information about the organ/segment like its name, layer and label value.
            The metadata dictionary is formatted as follows :

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
        segmentation_metadata = {}
        for segment in self._segments:
            organ_name = self._segments_names_associated_to_their_respective_organ[segment.name]
            segmentation_metadata[organ_name] = segment

        return segmentation_metadata

    def _get_the_label_map_of_a_specific_segment(self, segment: SegmentDataModel) -> np.ndarray:
        """
        Dictionary of all the segment names associated to their respective organ.

        Parameters
        ----------
        segment : SegmentDataModel
            Segment data.

        Returns
        -------
        label_map : np.ndarray
            Binary label map of a specific segment.
        """
        if self._segmentation_array_dimension == 3:
            array = self.segmentation_array
        elif self._segmentation_array_dimension == 4:
            array = self.segmentation_array[segment.layer]
        else:
            raise ValueError(f"Segmentation array must be of dimension 3 or 4. Given array is of dimension "
                             f"{self._segmentation_array_dimension}.")

        label_map = np.zeros_like(array)
        segment_values_idx = np.where(array == segment.label_value)
        label_map[segment_values_idx] = 1

        return label_map

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
        label_maps = {}
        for segment in self._segments:
            organ_name = self._segments_names_associated_to_their_respective_organ[segment.name]
            label_maps[organ_name] = self._get_the_label_map_of_a_specific_segment(segment=segment)

        return label_maps
