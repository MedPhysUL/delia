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

import numpy as np
import pydicom
import pydicom_seg
from rt_utils import RTStruct
import SimpleITK as sitk

from .base_segmentation_factory import BaseSegmentationFactory
from ....data_model import ImageDataModel
from .segment import Segment


class BaseDicomSegmentationFactory(BaseSegmentationFactory):
    """
    An abstract class used as a reference for all other segmentation classes that read data from DICOM files. These
    classes differ by the type of segmentation they are able to read. Indeed, the format of the segmentations may be
    different even if the file extension is the same, because there is multiple ways of representing a segment.
    """

    def __init__(
            self,
            image: ImageDataModel,
            path_to_segmentation: str
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
        """
        super().__init__(
            image=image,
            path_to_segmentation=path_to_segmentation
        )

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
            image: ImageDataModel,
            path_to_segmentation: str
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
        """
        super().__init__(
            image=image,
            path_to_segmentation=path_to_segmentation
        )

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


class RTStructSegmentationFactory(BaseDicomSegmentationFactory):
    """
    Class that defined the methods that are used to get the segments for the RT Struct type of segmentation.
    """

    def __init__(
            self,
            image: ImageDataModel,
            path_to_segmentation: str
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
        """
        super().__init__(
            image=image,
            path_to_segmentation=path_to_segmentation
        )

    @property
    def _reader(self) -> RTStruct:
        """
        Reader property.

        Returns
        -------
        reader : RTStruct
            RT Struct reader.
        """
        return RTStruct(
            series_data=[pydicom.dcmread(path) for path in self._image.paths_to_dicoms],
            ds=pydicom.dcmread(self._path_to_segmentation)
        )

    @property
    def segments(self) -> List[Segment]:
        """
        Segments property.

        Returns
        -------
        segments : List[Segment]
            List of all the segments.
        """
        segment_names = self._reader.get_roi_names()
        segments = []

        for organ_name in segment_names:
            array = self._reader.get_roi_mask_by_name(organ_name)
            array = np.multiply(array, 1)
            array = array.transpose(2, 0, 1)

            simple_itk_label_map = sitk.GetImageFromArray(array)
            simple_itk_label_map.SetOrigin(self._image.simple_itk_image.GetOrigin())
            simple_itk_label_map.SetSpacing(self._image.simple_itk_image.GetSpacing())
            simple_itk_label_map.SetDirection(self._image.simple_itk_image.GetDirection())

            segments.append(Segment(name=organ_name, simple_itk_label_map=simple_itk_label_map))

        return segments
