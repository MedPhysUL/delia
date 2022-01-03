"""
    @file:              dicom_reader.py
    @Author:            Maxence Larose

    @Creation Date:     10/2021
    @Last modification: 01/2022

    @Description:       This file contains the DicomReader class which is used to read dicom files contained in a given
                        folder.
"""

import logging
from typing import Dict, List, NamedTuple

import pydicom
import SimpleITK as sitk

from src.data_model import ImageDataModel
from src.utils import check_validity_of_given_path


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
            path_to_dicom_folder: str
    ):
        """
        Constructor of the class DicomReader.

        Parameters
        ----------
        path_to_dicom_folder : str
            Path to the folder containing the patient dicom files.
        """
        super(DicomReader, self).__init__()
        self._path_to_dicom_folder = path_to_dicom_folder

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
            logging.info(loaded_dicom)

        return loaded_dicom

    @property
    def __series_ids(self) -> List[str]:
        """
        Get all series IDs from a patient's dicom folder.

        Returns
        -------
        series_ids : List[str]
            All series IDs contained in a patient folder.
        """
        series_reader = sitk.ImageSeriesReader()
        series_ids = series_reader.GetGDCMSeriesIDs(self._path_to_dicom_folder)

        if not series_ids:
            raise FileNotFoundError(f"Given directory {self._path_to_dicom_folder} does not contain a DICOM series.")

        return series_ids

    @property
    def __series_data_dict(self) -> Dict[str, SeriesData]:
        """
        Get the series data from series IDs and the path to the patient's dicom folder.

        Returns
        -------
        series_data_dict : Dict[str, SeriesData]
            Dictionary of the data from the selected series.
        """
        series_data_dict: Dict[str, DicomReader.SeriesData] = {}
        for idx, series_id in enumerate(self.__series_ids):
            series_reader = sitk.ImageSeriesReader()
            paths_to_dicoms_from_series = series_reader.GetGDCMSeriesFileNames(self._path_to_dicom_folder, series_id)

            path_to_first_dicom_of_series = paths_to_dicoms_from_series[0]
            loaded_dicom_header = self.get_dicom_header(path_to_dicom=path_to_first_dicom_of_series)
            series_description = loaded_dicom_header.SeriesDescription

            series_data = self.SeriesData(
                series_description=series_description,
                paths_to_dicoms_from_series=paths_to_dicoms_from_series,
                dicom_header=loaded_dicom_header
            )
            series_data_dict[series_id] = series_data

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

    def get_images_data(self) -> List[ImageDataModel]:
        """
        List of tuples containing 3D images array and their corresponding dicom header. Each element in the list
        corresponds to an image series.

        Returns
        -------
        image_data_list : List[ImageDataModel]
            A list of the patient's images data.
        """
        check_validity_of_given_path(path=self._path_to_dicom_folder)

        images_data = []
        for series_data in self.__series_data_dict.values():
            image = self.__get_3d_sitk_image_from_dicom_series(
                paths_to_dicoms_from_series=series_data.paths_to_dicoms_from_series
            )

            image_data = ImageDataModel(
                dicom_header=series_data.dicom_header,
                simple_itk_image=image
            )

            images_data.append(image_data)

        return images_data
