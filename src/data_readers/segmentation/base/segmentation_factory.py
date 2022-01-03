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


class SegmentationFactory(ABC):
    """
    An abstract class that is used as a reference for all other segmentation classes that read data and build a
    Segmentation object from it.
    """

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
