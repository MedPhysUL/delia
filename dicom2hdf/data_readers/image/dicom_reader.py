"""
    @file:              dicom_reader.py
    @Author:            Maxence Larose

    @Creation Date:     10/2021
    @Last modification: 03/2022

    @Description:       This file contains the DicomReader class which is used to read dicom files contained in a given
                        folder.
"""

import logging
import os
from typing import Dict, List, NamedTuple, Set

import pydicom
import SimpleITK as sitk

from dicom2hdf.data_model import ImageDataModel
from dicom2hdf.data_readers.segmentation.segmentation_strategy import SegmentationStrategies
from dicom2hdf.utils import is_path_valid

_logger = logging.getLogger(__name__)


class DicomReader:
    """
    A class used to read dicom files contained in a given folder.
    """

    class SeriesData(NamedTuple):
        """
        Series description namedtuple to simplify management of values.
        """
        series_description: str
        paths_to_dicoms_from_series: List[str]
        dicom_header: pydicom.dataset.FileDataset

    def __init__(
            self,
            path_to_patient_folder: str
    ):
        """
        Constructor of the class DicomReader.

        Parameters
        ----------
        path_to_patient_folder : str
            Path to the folder containing the patient DICOM files.
        """
        super(DicomReader, self).__init__()

        is_path_valid(path=path_to_patient_folder)
        self._path_to_patient_folder = path_to_patient_folder

        self._images_series_data_dict = {}
        self._segmentations_series_data_dict = {}
        self.__series_data_dict = self.__get_series_data_dict()

    @staticmethod
    def get_dicom_header(
            path_to_dicom: str,
            show: bool = False
    ) -> pydicom.dataset.FileDataset:
        """
        Get a dicom header given the path to the dicom.

        Parameters
        ----------
        path_to_dicom : str
            The path to the dicom file.
        show : bool
            Show dicom header in console.

        Returns
        -------
        loaded_dicom : pydicom.dataset.FileDataset
            Loaded DICOM dataset.
        """
        loaded_dicom = pydicom.dcmread(path_to_dicom, stop_before_pixels=True)

        if show:
            _logger.info(loaded_dicom)

        return loaded_dicom

    def __get_paths_to_dicom_folders(self) -> List[str]:
        """
        List of paths to the folders that contain the DICOM files.

        Returns
        -------
        paths_to_dicom_folders : List[str]
            List of paths to the folders that contain the DICOM files.
        """
        paths_to_dicom_folders = []
        for path_to_folder, _, files in os.walk(self._path_to_patient_folder):
            if files:
                paths_to_dicom_folders.append(path_to_folder)

        return paths_to_dicom_folders

    @staticmethod
    def __get_series_ids(path_to_dicom_folder: str) -> List[str]:
        """
        Get all series IDs from a patient's dicom folder.

        Parameters
        ----------
        path_to_dicom_folder : str
            Path to a folder containing only DICOM files.

        Returns
        -------
        series_ids : List[str]
            All series IDs contained in a patient folder.
        """
        series_reader = sitk.ImageSeriesReader()
        series_ids = series_reader.GetGDCMSeriesIDs(path_to_dicom_folder)

        if not series_ids:
            raise FileNotFoundError(f"Given directory {path_to_dicom_folder} does not contain a DICOM series.")

        return series_ids

    def __get_series_data_dict(self) -> Dict[str, SeriesData]:
        """
        Get the series data from series IDs and the path to the patient's dicom folders.

        Returns
        -------
        series_data_dict : Dict[str, SeriesData]
            Dictionary of the data from the selected series.
        """
        series_data_dict: Dict[str, DicomReader.SeriesData] = {}
        all_patient_ids: Set[str] = set()
        for path_to_dicom_folder in self.__get_paths_to_dicom_folders():
            for idx, series_id in enumerate(self.__get_series_ids(path_to_dicom_folder)):
                series_reader = sitk.ImageSeriesReader()
                paths_to_dicoms_from_series = series_reader.GetGDCMSeriesFileNames(path_to_dicom_folder, series_id)

                path_to_first_dicom_of_series = paths_to_dicoms_from_series[0]
                loaded_dicom_header = self.get_dicom_header(path_to_dicom=path_to_first_dicom_of_series)
                all_patient_ids.add(loaded_dicom_header.PatientID)

                series_data = self.SeriesData(
                    series_description=loaded_dicom_header.SeriesDescription,
                    paths_to_dicoms_from_series=paths_to_dicoms_from_series,
                    dicom_header=loaded_dicom_header
                )
                series_data_dict[series_id] = series_data

            if len(all_patient_ids) != 1:
                raise AssertionError(f"All DICOM files in the same folder must belong to the same patient. This is not the "
                                     f"case for the patient whose data is currently being downloaded since the identifiers "
                                     f"{all_patient_ids} are found in their folder.")

            for series_id, series_data in series_data_dict.items():
                if series_data.dicom_header.Modality in SegmentationStrategies.get_available_modalities():
                    self._segmentations_series_data_dict[series_id] = series_data
                else:
                    self._images_series_data_dict[series_id] = series_data

        return series_data_dict

    @staticmethod
    def __get_3d_sitk_image_from_dicom_series(
            paths_to_dicoms_from_series: List[str],
    ) -> sitk.Image:
        """
        Get a 3D image array from a list of dicom paths associated to the same series.

        Parameters
        ----------
        paths_to_dicoms_from_series : List[str]
            A list of the paths to each dicom contained in the series.

        Returns
        -------
        image : sitk.Image
            3D SimpleITK image obtained from the series.
        """
        series_reader = sitk.ImageSeriesReader()
        series_reader.SetFileNames(paths_to_dicoms_from_series)

        image = series_reader.Execute()

        return image

    def get_dicom_headers(self, remove_segmentations: bool = False) -> List[pydicom.dataset.FileDataset]:
        """
        List of all the patient's dicom headers.

        Parameters
        ----------
        remove_segmentations : bool
            Whether or not to keep the segmentation files headers, default = False.

        Returns
        -------
        dicom_headers : List[pydicom.dataset.FileDataset]
            A list of the patient's DICOM headers.
        """
        dicom_headers = []
        for idx, series_data in enumerate(self.__series_data_dict.values()):
            if idx == 0:
                _logger.info(f"Patient ID : {series_data.dicom_header.PatientID}")
                _logger.debug(f"Path to images folder : {self._path_to_patient_folder}")

            _logger.debug(f"  Series description : {series_data.series_description}")

            if not remove_segmentations:
                dicom_headers.append(series_data.dicom_header)
            elif remove_segmentations:
                if series_data.dicom_header.Modality not in SegmentationStrategies.get_available_modalities():
                    dicom_headers.append(series_data.dicom_header)

        return dicom_headers

    def get_images_data(self, remove_segmentations: bool = False) -> List[ImageDataModel]:
        """
        List of tuples containing simpleITK 3D images array and their corresponding dicom header. Each element in the
        list corresponds to an image series.

        Parameters
        ----------
        remove_segmentations : bool
            Whether or not to keep the segmentation files headers, default = False.

        Returns
        -------
        image_data_list : List[ImageDataModel]
            A list of the patient's images data.
        """
        images_data = []
        for idx, series_data in enumerate(self.__series_data_dict.values()):

            if idx == 0:
                _logger.info(f"Series description found in the patient's images folder :")
            _logger.info(f"  Series description {idx + 1}: {series_data.series_description}")

            try:
                image = self.__get_3d_sitk_image_from_dicom_series(
                    paths_to_dicoms_from_series=series_data.paths_to_dicoms_from_series
                )

                image_data = ImageDataModel(
                    dicom_header=series_data.dicom_header,
                    simple_itk_image=image
                )

                if not remove_segmentations:
                    images_data.append(image_data)
                elif remove_segmentations:
                    if series_data.dicom_header.Modality not in SegmentationStrategies.get_available_modalities():
                        images_data.append(image_data)

            except RuntimeError as e:
                _logger.error(f"      RuntimeError : {e}. Simple ITK raised an error while loading the series named "
                              f"{series_data.series_description}. This series is therefore ignored.")

        return images_data
