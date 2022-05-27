"""
    @file:              patient_dataset.py
    @Author:            Maxence Larose

    @Creation Date:     10/2021
    @Last modification: 03/2022

    @Description:       This file contains the PatientDataset class that is used to interact with an hdf5 file dataset.
                        The main purpose of this class is to create an hdf5 file dataset from multiple patients dicom
                        files and their segmentation. This class also allows the user to interact with an existing hdf5
                        file dataset through queries.
"""

import logging
import os

import h5py
import json
import SimpleITK as sitk
from typing import Dict, List, Optional, Sequence, Tuple, Union

from dicom2hdf.data_generators.patients_data_generator import PatientsDataGenerator, PatientWhoFailed
from dicom2hdf.data_model import ImageAndSegmentationDataModel
from dicom2hdf.processing.transforms import BaseTransform

_logger = logging.getLogger(__name__)


class PatientsDataset:
    """
    A class that is used to interact with a patients dataset. The main purpose of this class is to create an hdf5 file
    dataset from multiple patients dicom files and their segmentation. This class also allows the user to interact with
    an existing hdf5 file dataset through queries.
    """

    def __init__(
            self,
            path_to_dataset: str,
    ):
        """
        Used to initialize the path to the dataset.

        Parameters
        ----------
        path_to_dataset : str
            Path to dataset.
        """
        self.path_to_dataset = path_to_dataset

    @property
    def path_to_dataset(self) -> str:
        """
        Path to dataset.

        Returns
        -------
        path_to_dataset : str
            Path to dataset containing modality and organ names.
        """
        return self._path_to_dataset

    @path_to_dataset.setter
    def path_to_dataset(self, path_to_dataset: str) -> None:
        """
        Path to dataset.

        Parameters
        ----------
        path_to_dataset : str
            Path to dataset.
        """
        if path_to_dataset.endswith(".h5"):
            self._path_to_dataset = path_to_dataset
        else:
            self._path_to_dataset = f"{path_to_dataset}.h5"

    def _check_authorization_of_dataset_creation(
            self,
            overwrite_dataset: bool
    ) -> None:
        """
        Check if dataset's creation is allowed.

        Parameters
        ----------
        overwrite_dataset : bool
            Overwrite existing dataset.
        """
        if os.path.exists(self.path_to_dataset):
            if not overwrite_dataset:
                raise FileExistsError("The dataset already exists. You may overwrite it using "
                                      "overwrite_dataset = True.")
            else:
                _logger.info(f"Overwriting HDF5 dataset with path : {self.path_to_dataset}")
        else:
            _logger.info(f"Writing HDF5 dataset with path : {self.path_to_dataset}")

    @staticmethod
    def _add_sitk_image_attributes_to_hdf5_group(
            patient_image_data: ImageAndSegmentationDataModel,
            group: h5py.Group
    ) -> None:
        """
        Add Simple ITK image information as attributes in the given HDF5 group.

        Parameters
        ----------
        patient_image_data : ImageAndSegmentationDataModel
            A named tuple grouping the patient data retrieved from his dicom files and the segmentation data retrieved
            from the segmentation file.
        group : h5py.Group
            An hdf5 group.
        """
        group.attrs.create(name="Size", data=patient_image_data.image.simple_itk_image.GetSize())
        group.attrs.create(name="Origin", data=patient_image_data.image.simple_itk_image.GetOrigin())
        group.attrs.create(name="Spacing", data=patient_image_data.image.simple_itk_image.GetSpacing())
        group.attrs.create(name="Direction", data=patient_image_data.image.simple_itk_image.GetDirection())
        group.attrs.create(name="Pixel Type", data=patient_image_data.image.simple_itk_image.GetPixelIDTypeAsString())

    @staticmethod
    def _add_dicom_attributes_to_hdf5_group(
            patient_image_data: ImageAndSegmentationDataModel,
            group: h5py.Group,
            tags_to_use_as_attributes: List[Tuple[int, int]],
    ) -> None:
        """
        Add the specified DICOM tags as attributes in the given HDF5 group.

        Parameters
        ----------
        patient_image_data : ImageAndSegmentationDataModel
            A named tuple grouping the patient data retrieved from his dicom files and the segmentation data retrieved
            from the segmentation file.
        group : h5py.Group
            An hdf5 group.
        tags_to_use_as_attributes : List[Tuple[int, int]]
            List of DICOM tags to add as series attributes in the HDF5 dataset.
        """
        for tag in tags_to_use_as_attributes:
            dicom_data_element = patient_image_data.image.dicom_header[tag]
            group.attrs.create(name=dicom_data_element.name, data=dicom_data_element.repval)

    def create_hdf5_dataset(
            self,
            path_to_patients_folder: str,
            series_descriptions: Optional[Union[str, Dict[str, List[str]]]] = None,
            tags_to_use_as_attributes: Optional[List[Tuple[int, int]]] = None,
            add_sitk_image_metadata_as_attributes: bool = True,
            transforms: Optional[Sequence[BaseTransform]] = None,
            overwrite_dataset: bool = False
    ) -> List[PatientWhoFailed]:
        """
        Create an hdf5 file dataset from multiple patients dicom files and their segmentation and get patient's images
        from this dataset. The goal is to create an object from which it is easier to obtain patient images and their
        segmentation than separated dicom files and segmentation files.

        Parameters
        ----------
        path_to_patients_folder : str
            The path to the folder that contains all the patients' folders.
        tags_to_use_as_attributes : List[Tuple[int, int]]
            List of DICOM tags to add as series attributes in the HDF5 dataset.
        series_descriptions : Optional[Union[str, Dict[str, List[str]]]], default = None.
            A dictionary that contains the series descriptions of the images that needs to be extracted from the
            patient's file. Keys are arbitrary names given to the images we want to add and values are lists of
            series descriptions. The images associated with these series descriptions do not need to have a
            corresponding segmentation. Note that it can be specified as a path to a json dictionary that contains the
            series descriptions.
        add_sitk_image_metadata_as_attributes : bool, default = True.
            Keep Simple ITK image information as attributes in the corresponding series.
        transforms : Optional[Sequence[BaseTransform]]
            A sequence of transformations to apply to images and segmentations.
        overwrite_dataset : bool, default = False.
            Overwrite existing dataset.

        Returns
        -------
        patients_who_failed : List[PatientWhoFailed]
            List of patients with one or more images not added to the HDF5 dataset due to the absence of the series in
            the patient record.
        """
        self._check_authorization_of_dataset_creation(overwrite_dataset=overwrite_dataset)

        if tags_to_use_as_attributes is None:
            tags_to_use_as_attributes = []

        hf = h5py.File(self.path_to_dataset, "w")

        patient_data_generator = PatientsDataGenerator(
            path_to_patients_folder=path_to_patients_folder,
            series_descriptions=series_descriptions,
            transforms=transforms
        )

        number_of_patients = len(patient_data_generator)
        for patient_idx, patient_dataset in enumerate(patient_data_generator):
            patient_id = patient_dataset.patient_id
            patient_group = hf.create_group(name=patient_id)

            for image_idx, patient_image_data in enumerate(patient_dataset.data):
                image_array = sitk.GetArrayFromImage(patient_image_data.image.simple_itk_image)
                transposed_image_array = image_array.transpose(1, 2, 0)

                series_group = patient_group.create_group(name=str(image_idx))

                self._add_dicom_attributes_to_hdf5_group(patient_image_data, series_group, tags_to_use_as_attributes)

                if add_sitk_image_metadata_as_attributes:
                    self._add_sitk_image_attributes_to_hdf5_group(patient_image_data, series_group)

                series_group.create_dataset(
                    name="image",
                    data=transposed_image_array
                )

                series_group.create_dataset(
                    name="dicom_header",
                    data=json.dumps(patient_image_data.image.dicom_header.to_json_dict())
                )

                if patient_image_data.segmentation:
                    for organ, simple_itk_label_map in patient_image_data.segmentation.simple_itk_label_maps.items():
                        numpy_array_label_map = sitk.GetArrayFromImage(simple_itk_label_map)
                        transposed_numpy_array_label_map = numpy_array_label_map.transpose(1, 2, 0)
                        series_group.create_dataset(
                            name=f"{organ}_label_map",
                            data=transposed_numpy_array_label_map
                        )

            _logger.info(f"Progress : {patient_idx + 1}/{number_of_patients} patients added to dataset.")

        patient_data_generator.close()

        return patient_data_generator.patients_who_failed
