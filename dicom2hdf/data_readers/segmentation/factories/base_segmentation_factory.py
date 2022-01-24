"""
    @file:              segmentation_factory.py
    @Author:            Maxence Larose

    @Creation Date:     12/2021
    @Last modification: 01/2022

    @Description:       This file contains the class SegmentationFactory that is used as an abstract class used as a
                        reference for all other segmentation classes that read data and build a Segmentation object
                        from it.
"""

from abc import ABC, abstractmethod
from typing import List

from .segment import Segment
from .segmentation import Segmentation


class BaseSegmentationFactory(ABC):
    """
    An abstract class that is used as a reference for all other segmentation classes that read data and build a
    Segmentation object from it.
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
        """
        self._path_to_segmentation = path_to_segmentation

    @property
    @abstractmethod
    def segments(self) -> List[Segment]:
        """
        Abstract segments property.

        Returns
        -------
        segments : List[Segment]
            List of all the segments.
        """
        pass

    def create_segmentation(self) -> Segmentation:
        """
        Creates a Segmentation using the list of Segments.

        Returns
        -------
        segmentation : Segmentation
            Segmentation.
        """
        return Segmentation(segments=self.segments)
