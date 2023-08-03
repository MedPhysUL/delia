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
from typing import List, Optional

from ....utils.data_model import ImageDataModel
from .segment import Segment
from .segmentation import Segmentation


class BaseSegmentationFactory(ABC):
    """
    An abstract class that is used as a reference for all other segmentation classes that read data and build a
    Segmentation object from it.
    """

    def __init__(
            self,
            image: ImageDataModel,
            path_to_segmentation: str,
            organs: Optional[List[str]] = None
    ):
        """
        Used to load the segmentation data from the path to segmentation.

        Parameters
        ----------
        image : ImageDataModel
            A named tuple grouping the patient's dicom header, its medical image as a simpleITK image and a sequence of
            the paths to each dicom contained in the series.
        path_to_segmentation : str
            The path to the segmentation file.
        organs : Optional[List[str]]
            The set of organs to save.
        """
        self._image = image
        self._path_to_segmentation = path_to_segmentation
        self._organs = organs

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
