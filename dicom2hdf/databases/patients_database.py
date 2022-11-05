"""
    @file:              patients_database.py
    @Author:            Maxence Larose

    @Creation Date:     10/2021
    @Last modification: 10/2022

    @Description:       This file contains the PatientDatabase class that is used to interact with an hdf5 file
                        database. The main purpose of this class is to create an hdf5 file database from multiple
                        patients dicom files and their segmentation. This class also allows the user to interact with
                        an existing hdf5 file database through queries.
"""

import logging
import os
from typing import List, Optional, Tuple, Union

import h5py
import json
import numpy as np
import SimpleITK as sitk

from dicom2hdf.data_generators.patients_data_generator import PatientsDataGenerator, PatientWhoFailed
from dicom2hdf.data_model import ImageAndSegmentationDataModel

_logger = logging.getLogger(__name__)


class PatientsDatabase:
    """
    A class that is used to interact with a patients database. The main purpose of this class is to create an hdf5 file
    database from multiple patients dicom files and their segmentation. This class also allows the user to interact with
    an existing hdf5 file database through queries.
    """

    DICOM_HEADER = "Dicom_header"
    IMAGE = "Image"
    MODALITY = "Modality"
    TRANSFORMS = "Transforms"

    def __init__(
            self,
            path_to_database: str,
    ):
        """
        Used to initialize the path to the database.

        Parameters
        ----------
        path_to_database : str
            Path to database.
        """
        self.path_to_database = path_to_database

    @property
    def path_to_database(self) -> str:
        """
        Path to database.

        Returns
        -------
        path_to_database : str
            Path to database containing modality and organ names.
        """
        return self._path_to_database

    @path_to_database.setter
    def path_to_database(self, path_to_database: str) -> None:
        """
        Path to database.

        Parameters
        ----------
        path_to_database : str
            Path to database.
        """
        if path_to_database.endswith(".h5"):
            self._path_to_database = path_to_database
        else:
            self._path_to_database = f"{path_to_database}.h5"

    def __getitem__(self, patient_id: Union[List[str], str]) -> Union[List[h5py.Group], h5py.Group]:
        """
        Get a patient group given the patient ID.

        Parameters
        ----------
        patient_id : str
            Patient ID.
        """
        if os.path.exists(self.path_to_database):
            file = h5py.File(self.path_to_database, mode="r")

            if isinstance(patient_id, str):
                return file[patient_id]
            elif isinstance(patient_id, list):
                return [file[uid] for uid in patient_id]
            else:
                raise AssertionError(f"Patient ID should be a list of patient ids (List[str]) or a single patient id "
                                     f"(str). Received {type(patient_id)}.")
        else:
            raise AssertionError(f"Database with path {self.path_to_database} doesn't exist. Use 'create'.")

    def _check_authorization_of_database_creation(
            self,
            overwrite_database: bool
    ) -> None:
        """
        Check if database's creation is allowed.

        Parameters
        ----------
        overwrite_database : bool
            Overwrite existing database.
        """
        if os.path.exists(self.path_to_database):
            if not overwrite_database:
                raise FileExistsError("The database already exists. You may overwrite it using "
                                      "overwrite_database = True.")
            else:
                _logger.info(f"Overwriting HDF5 database with path : {self.path_to_database}")
        else:
            _logger.info(f"Writing HDF5 database with path : {self.path_to_database}")

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
            List of DICOM tags to add as series attributes in the HDF5 database.
        """
        for tag in tags_to_use_as_attributes:
            dicom_data_element = patient_image_data.image.dicom_header[tag]

            if type(dicom_data_element.value) == str:
                data = dicom_data_element.value
            else:
                data = dicom_data_element.repval

            group.attrs.create(name=dicom_data_element.name, data=data)

    @staticmethod
    def _is_shape_valid(shape: np.shape) -> bool:
        """
        Check if the given shape is in the right format for the hdf5 database.

        Parameters
        ----------
        shape : np.shape
            An numpy array's shape.

        Returns
        -------
        valid : bool
            Whether the shape is valid or not.
        """
        if shape[1] == shape[2] and shape[0] != shape[1] and shape[0] != shape[2]:
            return False
        else:
            return True

    def _transpose(self, array: np.ndarray) -> np.ndarray:
        """
        Transpose an array if its shape is not valid for the hdf5 database format.

        Parameters
        ----------
        array : np.ndarray
            An numpy array.

        Returns
        -------
        transposed_array : np.ndarray
            The original array or the transposed array depending on its input shape.
        """
        if self._is_shape_valid(array.shape):
            return array
        else:
            return array.transpose((1, 2, 0))

    def create(
            self,
            patients_data_generator: PatientsDataGenerator,
            tags_to_use_as_attributes: Optional[List[Tuple[int, int]]] = None,
            add_sitk_image_metadata_as_attributes: bool = True,
            overwrite_database: bool = False
    ) -> List[PatientWhoFailed]:
        """
        Create an hdf5 file database from multiple patients dicom files and their segmentation. The goal is to create
        an object from which it is easier to obtain patient images and their segmentation than separated dicom files
        and segmentation files.

        Parameters
        ----------
        patients_data_generator : PatientsDataGenerator
            An object used to iterate on multiple patients' dicom files and segmentation files using the
            PatientDataReader to obtain all patients' data.
        tags_to_use_as_attributes : List[Tuple[int, int]]
            List of DICOM tags to add as series attributes in the HDF5 database.
        add_sitk_image_metadata_as_attributes : bool, default = True.
            Keep Simple ITK image information as attributes in the corresponding series.
        overwrite_database : bool, default = False.
            Overwrite existing database.

        Returns
        -------
        patients_who_failed : List[PatientWhoFailed]
            List of patients with one or more images not added to the HDF5 database due to the absence of the series in
            the patient record.
        """
        self._check_authorization_of_database_creation(overwrite_database=overwrite_database)

        if tags_to_use_as_attributes is None:
            tags_to_use_as_attributes = []

        hf = h5py.File(self.path_to_database, "w")

        number_of_patients = len(patients_data_generator)
        for patient_idx, patient_dataset in enumerate(patients_data_generator):
            patient_id = patient_dataset.patient_id
            patient_group = hf.create_group(name=patient_id)

            for image_idx, patient_image_data in enumerate(patient_dataset.data):
                series_group = patient_group.create_group(name=str(image_idx))

                self._add_dicom_attributes_to_hdf5_group(patient_image_data, series_group, tags_to_use_as_attributes)

                if add_sitk_image_metadata_as_attributes:
                    self._add_sitk_image_attributes_to_hdf5_group(patient_image_data, series_group)

                series_group.create_dataset(
                    name=self.DICOM_HEADER,
                    data=json.dumps(patient_image_data.image.dicom_header.to_json_dict())
                )

                image_array = sitk.GetArrayFromImage(patient_image_data.image.simple_itk_image)

                series_group.create_dataset(
                    name=self.IMAGE,
                    data=self._transpose(image_array)
                )

                if patient_image_data.segmentations:
                    for segmentation_idx, segmentation in enumerate(patient_image_data.segmentations):
                        segmentation_group = series_group.create_group(name=str(segmentation_idx))
                        segmentation_group.attrs.create(name=self.MODALITY, data=segmentation.modality)

                        for organ, simple_itk_label_map in segmentation.simple_itk_label_maps.items():
                            numpy_array_label_map = sitk.GetArrayFromImage(simple_itk_label_map)

                            segmentation_group.create_dataset(
                                name=organ,
                                data=self._transpose(numpy_array_label_map),
                                dtype=np.int8
                            )

            for idx, transform in enumerate(patient_dataset.transforms_history.history):
                patient_group.attrs.create(
                    name=f"{self.TRANSFORMS}_{idx}",
                    data=json.dumps(
                        obj=transform,
                        default=patient_dataset.transforms_history.serialize
                    )
                )

            _logger.info(f"Progress : {patient_idx + 1}/{number_of_patients} patients added to database.")

        patients_data_generator.close()

        return patients_data_generator.patients_who_failed
