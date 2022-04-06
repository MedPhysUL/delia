"""
    @file:              dicom_segmentation_factory.py
    @Author:            Maxence Larose

    @Creation Date:     01/2022
    @Last modification: 03/2022

    @Description:       This file contains the abstract class BaseDicomSegmentationFactory and all factories that
                        inherit from this class.
"""

from abc import abstractmethod
from typing import List

import pydicom
import pydicom_seg

from .segment import Segment
from .base_segmentation_factory import BaseSegmentationFactory


class BaseDicomSegmentationFactory(BaseSegmentationFactory):
    """
    An abstract class used as a reference for all other segmentation classes that read data from DICOM files. These
    classes differ by the type of segmentation they are able to read. Indeed, the format of the segmentations may be
    different even if the file extension is the same, because there is multiple ways of representing a segment.
    """

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
        """
        super().__init__(path_to_segmentation=path_to_segmentation)

        self._dicom: pydicom.FileDataset = pydicom.dcmread(path_to_segmentation)

    @abstractmethod
    def segments(self) -> List[Segment]:
        """
        Segments property.

        Returns
        -------
        segments : List[Segment]
            List of all the segments.
        """
        raise NotImplementedError


class DicomSEGSegmentationFactory(BaseDicomSegmentationFactory):
    """
    Class that defined the methods that are used to get the segments for the DICOM-SEG type of segmentation.
    """

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
        """
        super().__init__(path_to_segmentation=path_to_segmentation)

    @property
    def _reader(self) -> pydicom_seg.SegmentReader:
        """
        Reader property.

        Returns
        -------
        reader : pydicom_seg.SegmentReader
            DICOM-SEG reader.
        """
        return pydicom_seg.SegmentReader()

    @property
    def segments(self) -> List[Segment]:
        """
        Segments property.

        Returns
        -------
        segments : List[Segment]
            List of all the segments.
        """
        result = self._reader.read(self._dicom)

        segments = []
        for segment_number, dicom_header in result.segment_infos.items():
            if dicom_header.__contains__("SegmentLabel"):
                organ_name = dicom_header.SegmentLabel
            else:
                organ_name = dicom_header.SegmentDescription

            simple_itk_label_map = result.segment_image(segment_number)

            segments.append(Segment(name=organ_name, simple_itk_label_map=simple_itk_label_map))

        return segments
