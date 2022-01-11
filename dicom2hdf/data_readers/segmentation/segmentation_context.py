"""
    @file:              segmentation_context.py
    @Author:            Maxence Larose

    @Creation Date:     10/2021
    @Last modification: 01/2022

    @Description:       This file contains the class SegmentationContext that is used as a context class where
                        strategies are types of ways to load the segmentation data, or more precisely, types of
                        segmentation object factory.
"""

from typing import Dict, List

from .segmentation_strategy import SegmentationStrategy, SegmentationStrategies
from .factories.segmentation import Segmentation


class SegmentationContext:
    """
    A class used as a context class where strategies are types of ways to load the segmentation data, or more precisely,
    types of segmentation object factory. Strategies are entirely defined by the extension of the given file and so, by
    the path of the segmentation.
    """

    def __init__(
            self,
            path_to_segmentation: str,
            organs: Dict[str, List[str]]
    ):
        """
        Constructor of the SegmentationContext class.

        Parameters
        ----------
        path_to_segmentation : str
            The path to the segmentation file.
        organs : Dict[str, List[str]]
            A dictionary that contains the organs and their associated segment names. Keys are arbitrary organ names
            and values are lists of possible segment names.
        """
        self._path_to_segmentation = path_to_segmentation
        self._organs = organs

    @property
    def path_to_segmentation(self) -> str:
        """
        Path to segmentation property.

        Returns
        -------
        path_to_segmentation : str
            The path to the segmentation file.
        """
        return self._path_to_segmentation

    @path_to_segmentation.setter
    def path_to_segmentation(self, path_to_segmentation: str) -> None:
        """
        Path to segmentation setter.

        Parameters
        ----------
        path_to_segmentation : str
            The path to the segmentation file.
        """
        self._path_to_segmentation = path_to_segmentation

    @property
    def segmentation_strategy(self) -> SegmentationStrategy:
        """
        Segmentation strategy corresponding to the given segmentation file extension.

        Returns
        -------
        segmentation_strategy : SegmentationStrategy
            Segmentation strategy.
        """
        possible_segmentation_strategies: List[SegmentationStrategy] = []
        for segmentation_category in list(SegmentationStrategies):
            if self.path_to_segmentation.endswith(segmentation_category.file_extension):
                possible_segmentation_strategies.append(segmentation_category)

        return max(possible_segmentation_strategies, key=len)

    @property
    def _segmentation_factory_instance(self) -> SegmentationStrategy.factory:
        """
        The segmentation factory instance corresponding to the class of the given segmentation category.

        Returns
        -------
        _segmentation_factory_instance : SegmentationStrategy.factory
            Factory class instance used to get the label maps and the segmentation metadata from a segmentation file.
        """
        return self.segmentation_strategy.factory(
            path_to_segmentation=self.path_to_segmentation,
            organs=self._organs
        )

    def create_segmentation(self) -> Segmentation:
        """
        Creates a Segmentation object.

        Returns
        -------
        segmentation : Segmentation
            Segmentation.
        """
        return self._segmentation_factory_instance.create_segmentation()
