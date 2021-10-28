import logging
from typing import Dict, List, Union, NamedTuple

import pydicom
import SimpleITK as sitk

from src.data_model import ImageDataModel, ImageAndSegmentationDataModel, PatientDataModel
from src.utils import check_validity_of_given_path


class DicomReader:

    class SeriesData(NamedTuple):
        series_description: str
        paths_to_dicoms_from_series: List[str]
        dicom_header: pydicom.dataset.FileDataset

    def __init__(self, *args, **kwargs):
        """
        Used to load one or multiple dicom files and apply different queries on the loaded files like obtain a patient
        image dataset from those dicom files.
        """
        super(DicomReader, self).__init__(*args, **kwargs)

    @staticmethod
    def _get_dicom_header(
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

    @staticmethod
    def __get_series_ids_from_path_to_dicom_folder(
            path_to_dicom_folder: str
    ) -> List[str]:
        """
        Get all series IDs from a patient's dicom folder.

        Parameters
        ----------
        path_to_dicom_folder : str
            Path to the folder containing the patient's dicom files.

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

    def __get_selected_series_data_from_series_ids_and_path_to_dicom_folder(
            self,
            series_ids: List[str],
            path_to_dicom_folder: str
    ) -> Dict[str, SeriesData]:
        """
        Get the selected series data from series IDs and the path to the patient's dicom folder. The series are
        selected if the series description corresponds to one of the description available in the Modality class.

        Parameters
        ----------
        series_ids : List[str]
            All series IDs contained in a patient folder.
        path_to_dicom_folder : str
            Path to the folder containing the patient's dicom files.

        Returns
        -------
        selected_series_data : Dict[str, SeriesData]
            Dictionary of the data from the selected series.
        """
        all_series_description: List[str] = []
        selected_series_data: Dict[str, DicomReader.SeriesData] = {}
        for idx, series_id in enumerate(series_ids):
            series_reader = sitk.ImageSeriesReader()
            paths_to_dicoms_from_series = series_reader.GetGDCMSeriesFileNames(path_to_dicom_folder, series_id)

            path_to_first_dicom_of_series = paths_to_dicoms_from_series[0]
            loaded_dicom_header = self._get_dicom_header(path_to_dicom=path_to_first_dicom_of_series)
            modality, series_description = loaded_dicom_header.Modality, loaded_dicom_header.SeriesDescription
            all_series_description.append(series_description)

            series_data = self.SeriesData(
                series_description=series_description,
                paths_to_dicoms_from_series=paths_to_dicoms_from_series,
                dicom_header=loaded_dicom_header
            )
            selected_series_data[series_id] = series_data

        return selected_series_data

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

    def __generate_3d_images_dataset_from_patient_series(
            self,
            path_to_dicom_folder: str,
    ) -> Dict[str, Union[str, Dict[str, ImageAndSegmentationDataModel]]]:
        """
        Generate multiple 3D images array each corresponding to a specific modality. Images are generated from the dicom
        files contained in the given folder. The output patient data are formatted in a dictionary containing the
        patient's name and his images with their associated modality.

        Parameters
        ----------
        path_to_dicom_folder : str
            Path to the folder containing the patient dicom files.

        Returns
        -------
        image_dataset : dict
            A dictionary regrouping the patient's name, and his images with their associated modality and dicom header.
            This dictionary is formatted as follows :

                image_dataset = {
                    "patient_name": patient_name,
                    "data": {
                        modality (example: "CT"): ImageAndSegmentationDataModel,
                        modality (example: "PT"): ImageAndSegmentationDataModel,
                        ...
                    }
                }
        """
        check_validity_of_given_path(path=path_to_dicom_folder)
        series_ids = self.__get_series_ids_from_path_to_dicom_folder(path_to_dicom_folder=path_to_dicom_folder)

        selected_series_data = self.__get_selected_series_data_from_series_ids_and_path_to_dicom_folder(
            series_ids=series_ids,
            path_to_dicom_folder=path_to_dicom_folder
        )

        image_dataset = {}
        for series_data in selected_series_data.values():
            image = self.__get_3d_sitk_image_from_dicom_series(
                paths_to_dicoms_from_series=series_data.paths_to_dicoms_from_series
            )

            image_data = ImageDataModel(
                dicom_header=series_data.dicom_header,
                simple_itk_image=image
            )

            image_and_segmentation_data = ImageAndSegmentationDataModel(
                image=image_data
            )

            if image_dataset == {}:
                image_dataset = dict(
                    patient_name=str(series_data.dicom_header.PatientName),
                    data=[image_and_segmentation_data]
                )
            else:
                image_dataset["data"].append(image_and_segmentation_data)

        return image_dataset

    def _get_patient_image_data(self, path_to_dicom_folder: str, ) -> PatientDataModel:
        """
        Get the patient medical data from the path of the folder containing its dicom files.

        Parameters
        ----------
        path_to_dicom_folder : str
            Path to the folder containing the patient dicom files.

        Returns
        -------
        patient_image_data : PatientDataModel
            A named tuple grouping the patient's data extracted from its dicom files for each available modality. The
            segmentation data of the patient's medical image is set to "None" since it is not read by the dicom reader
            but rather by the segmentation reader.
        """
        image_dataset = self.__generate_3d_images_dataset_from_patient_series(path_to_dicom_folder=path_to_dicom_folder)

        patient_image_data = PatientDataModel(
            patient_name=image_dataset["patient_name"],
            data=image_dataset["data"]
        )

        return patient_image_data
