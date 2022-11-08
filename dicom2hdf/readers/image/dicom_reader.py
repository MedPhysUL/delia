"""
    @file:              dicom_reader.py
    @Author:            Maxence Larose

    @Creation Date:     10/2021
    @Last modification: 03/2022

    @Description:       This file contains the DicomReader class which is used to read dicom files contained in a given
                        folder.
"""

from collections import defaultdict
from glob import glob
import logging
import os
from typing import Dict, List, NamedTuple, Set

import pydicom
import SimpleITK as sitk

from dicom2hdf.utils.data_model import ImageDataModel
from dicom2hdf.readers.segmentation.segmentation_strategy import SegmentationStrategies
from dicom2hdf.utils.tools import is_path_valid

_logger = logging.getLogger(__name__)


class DicomReader:
    """
    A class used to read dicom files contained in a given folder.
    """

    UNKNOWN = "Unknown"

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

    @staticmethod
    def _get_series_description(dicom_header: pydicom.FileDataset) -> str:
        """
        Get Series Description of given DICOM header.

        Parameters
        ----------
        dicom_header : pydicom.dataset.FileDataset
            Loaded DICOM dataset.

        Returns
        -------
        series_description : str
            Series Description.
        """
        if hasattr(dicom_header, "SeriesDescription"):
            return dicom_header.SeriesDescription
        else:
            return DicomReader.UNKNOWN

    def __get_paths_to_dicoms_from_series(self, path_to_dicom_folder: str) -> Dict[str, List[str]]:
        """
        Get all series IDs from a patient's dicom folder.

        Parameters
        ----------
        path_to_dicom_folder : str
            Path to a folder containing only DICOM files.

        Returns
        -------
        paths_to_dicoms_from_series : Dict[str, List[str]]
            Dictionary of lists of paths to dicoms from each series.
        """
        paths = [
            y for x in os.walk(path_to_dicom_folder) for y in glob(os.path.join(x[0], '*')) if os.path.isfile(y) is True
        ]

        paths_and_headers_for_each_series = defaultdict(list)
        for path in paths:
            dicom_header = self.get_dicom_header(path_to_dicom=path)
            paths_and_headers_for_each_series[dicom_header.SeriesInstanceUID].append((path, dicom_header))

        paths_to_dicoms_from_series = defaultdict(list)
        for series_id, result in paths_and_headers_for_each_series.items():
            if len(result) != 1:
                if hasattr(result[1][1], "SliceLocation"):
                    paths_to_dicoms_from_series[series_id] = [
                        i[0] for i in sorted(result, key=lambda s: s[1].SliceLocation)
                    ]
                else:
                    paths_to_dicoms_from_series[series_id] = [
                        i[0] for i in result
                    ]
            else:
                paths_to_dicoms_from_series[series_id] = [result[0][0]]

        return paths_to_dicoms_from_series

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
        for series_id, paths in self.__get_paths_to_dicoms_from_series(self._path_to_patient_folder).items():
            path_to_first_dicom_of_series = paths[0]
            loaded_dicom_header = self.get_dicom_header(path_to_dicom=path_to_first_dicom_of_series)
            all_patient_ids.add(loaded_dicom_header.PatientID)

            series_data = self.SeriesData(
                series_description=self._get_series_description(loaded_dicom_header),
                paths_to_dicoms_from_series=paths,
                dicom_header=loaded_dicom_header
            )
            series_data_dict[series_id] = series_data

        if len(all_patient_ids) == 0:
            raise AssertionError(f"The patient folder must contain DICOM files. This is not the case for the patient "
                                 f"whose data is currently being downloaded since no DICOM files are found in its "
                                 f"folder.")
        elif len(all_patient_ids) > 1:
            raise AssertionError(f"All DICOM files in the same folder must belong to the same patient. This is not "
                                 f"the case for the patient whose data is currently being downloaded since the "
                                 f"identifiers {all_patient_ids} are found in their folder.")

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

    def get_images_data(
            self,
            remove_segmentations: bool = False
    ) -> List[ImageDataModel]:
        """
        List of tuples containing simpleITK 3D images array and their corresponding dicom header. Each element in the
        list corresponds to an image series.

        Parameters
        ----------
        remove_segmentations : bool
            Whether to keep the segmentation files headers, default = False.

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

            if remove_segmentations and (series_data.dicom_header.Modality in
                                         SegmentationStrategies.get_available_modalities()):
                pass
            elif series_data.series_description == DicomReader.UNKNOWN:
                pass
            else:
                try:
                    image = self.__get_3d_sitk_image_from_dicom_series(
                        paths_to_dicoms_from_series=series_data.paths_to_dicoms_from_series
                    )

                    image_data = ImageDataModel(
                        dicom_header=series_data.dicom_header,
                        simple_itk_image=image,
                        paths_to_dicoms=series_data.paths_to_dicoms_from_series
                    )

                    images_data.append(image_data)

                except RuntimeError as e:
                    _logger.error(f"      RuntimeError : {e}. Simple ITK raised an error while loading the series "
                                  f"named {series_data.series_description}. This series is therefore ignored.")

        return images_data
