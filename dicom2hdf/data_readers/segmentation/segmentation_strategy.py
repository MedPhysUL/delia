"""
    @file:              segmentation_strategy.py
    @Author:            Maxence Larose

    @Creation Date:     10/2021
    @Last modification: 01/2022

    @Description:       This file contains the class SegmentationStrategies that enumerates the available categories of
                        segmentation files.
"""

import enum
from typing import List, NamedTuple, Callable

from .factories.dicom_segmentation_factories import (DicomSEGSegmentationFactory, RTStructSegmentationFactory)


class SegmentationStrategy(NamedTuple):
    name: str
    modality: str
    factory: Callable


class SegmentationStrategies(enum.Enum):

    DICOM_SEG = SegmentationStrategy(
        name="dicom_seg",
        modality="SEG",
        factory=DicomSEGSegmentationFactory
    )

    RT_STRUCT = SegmentationStrategy(
        name="rt_struct",
        modality="RTSTRUCT",
        factory=RTStructSegmentationFactory
    )

    def __init__(self, *args):
        """
        Used to make sure that the segmentation strategies enumeration contains no strategy with the same modality.
        """
        cls = self.__class__

        if any(self.value.modality == member.value.modality for member in cls):
            first_member_name = self.name
            first_member_modality_value = self.value.modality
            second_member_name = cls(self.value).name
            second_member_modality_value = cls(self.value).value.modality

            raise ValueError(f"Aliases not allowed in the SegmentationStrategies Enum Class. The value assigned to the"
                             f" {first_member_name} attribute is {first_member_modality_value} and the value assigned "
                             f"to the {second_member_name} attribute is"
                             f" as the one assigned to the {second_member_name} attribute, since it is also "
                             f"{second_member_modality_value}.")

    @classmethod
    def get_available_modalities(cls) -> List[str]:
        """
        Available segmentation DICOM modalities.

        Returns
        -------
        available_modalities : List[str]
            Available modalities.
        """
        return [member.value.modality for member in cls]
