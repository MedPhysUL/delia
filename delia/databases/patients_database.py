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

from delia.extractors.patients_data_extractor import PatientsDataExtractor, PatientWhoFailed
from delia.utils.data_model import ImageAndSegmentationDataModel

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

        if os.path.exists(path_to_database):
            try:
                self._file = h5py.File(path_to_database, mode="r+")
            except OSError:
                self._file = h5py.File(path_to_database, mode="r")
        else:
            self._file = None

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

    def __getitem__(self, patient: Union[int, List[int], str, List[str]]) -> Union[List[h5py.Group], h5py.Group]:
        """
        Gets a patient group given the patient ID. This method returns a copy of the patient group.

        Parameters
        ----------
        patient : Union[int, List[int], str, List[str]]
            Patient ID (strings) or index (integers).
        """
        if os.path.exists(self.path_to_database):
            if isinstance(patient, int):
                file_keys = list(self._file.keys())
                patient = file_keys[patient]
            elif isinstance(patient, list):
                file_keys = list(self._file.keys())
                patient = [file_keys[p] if isinstance(p, int) else p for p in patient]

            if isinstance(patient, str):
                return self._file[patient]
            elif isinstance(patient, list):
                return [self._file[uid] for uid in patient]
            else:
                raise AssertionError(
                    f"Patient ID should be a list of patient ids (List[str]) or a single patient id (str). "
                    f"Received {type(patient)}."
                )
        else:
            raise AssertionError(f"Database with path {self.path_to_database} doesn't exist. Use 'create'.")

    def __len__(self) -> int:
        """
        Gets number of patients in the database of h5py.File.

        Returns
        -------
        length : int
            Number of patients in the database.
        """
        if self._file:
            return len(self._file.keys())
        else:
            return 0

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
                raise FileExistsError(
                    "The database already exists. You may overwrite it using overwrite_database = True."
                )
            else:
                self.close()
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
    def _transpose(array: np.ndarray) -> np.ndarray:
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
        return array.transpose((1, 2, 0))

    def create(
            self,
            patients_data_extractor: PatientsDataExtractor,
            tags_to_use_as_attributes: Optional[List[Tuple[int, int]]] = None,
            add_sitk_image_metadata_as_attributes: bool = True,
            organs_to_keep: Optional[Union[str, List[str]]] = None,
            overwrite_database: bool = False,
            transpose: bool = True,
            shallow_hierarchy: bool = False
    ) -> List[PatientWhoFailed]:
        """
        Create an hdf5 file database from multiple patients dicom files and their segmentation. The goal is to create
        an object from which it is easier to obtain patient images and their segmentation than separated dicom files
        and segmentation files.

        Parameters
        ----------
        patients_data_extractor : PatientsDataExtractor
            An object used to iterate on multiple patients' dicom files and segmentation files using the
            PatientDataReader to obtain all patients' data.
        tags_to_use_as_attributes : List[Tuple[int, int]]
            List of DICOM tags to add as series attributes in the HDF5 database.
        add_sitk_image_metadata_as_attributes : bool, default = True.
            Keep Simple ITK image information as attributes in the corresponding series.
        organs_to_keep : Optional[Union[str, List[str]]]
            Organ segmentations to keep in the database. By default, all organs are kept.
        overwrite_database : bool, default = False.
            Overwrite existing database.
        transpose : bool, default = True.
            Transpose the image array before using it.
        shallow_hierarchy : bool, default = False.
            Creates database with shallow hierarchy.

        Returns
        -------
        patients_who_failed : List[PatientWhoFailed]
            List of patients with one or more images not added to the HDF5 database due to the absence of the series in
            the patient record.
        """
        self._check_authorization_of_database_creation(overwrite_database=overwrite_database)

        if tags_to_use_as_attributes is None:
            tags_to_use_as_attributes = []
        if isinstance(organs_to_keep, str):
            organs_to_keep = [organs_to_keep]

        with h5py.File(self.path_to_database, "w") as file:
            patients_data_extractor.reset()
            number_of_patients = len(patients_data_extractor)
            for patient_idx, patient_dataset in enumerate(patients_data_extractor):
                patient_id = patient_dataset.patient_id
                patient_path = patient_dataset.patient_path

                if shallow_hierarchy is True:
                    patient_group = file
                else:
                    patient_group = file.create_group(name=patient_id)

                for image_idx, patient_image_data in enumerate(patient_dataset.data):

                    if shallow_hierarchy is True:
                        series_group = patient_group
                        image_name = os.path.basename(os.path.normpath(patient_path))
                    else:
                        series_group = patient_group.create_group(name=str(image_idx))
                        image_name = self.IMAGE

                    self._add_dicom_attributes_to_hdf5_group(
                        patient_image_data, series_group, tags_to_use_as_attributes
                    )

                    if add_sitk_image_metadata_as_attributes:
                        self._add_sitk_image_attributes_to_hdf5_group(patient_image_data, series_group)

                    series_group.create_dataset(
                        name=self.DICOM_HEADER,
                        data=json.dumps(patient_image_data.image.dicom_header.to_json_dict())
                    )

                    if transpose is True:
                        image_array = self._transpose(sitk.GetArrayFromImage(patient_image_data.image.simple_itk_image))
                    else:
                        image_array = sitk.GetArrayFromImage(patient_image_data.image.simple_itk_image)

                    data_set = series_group.create_dataset(
                        name=image_name,
                        data=image_array
                    )

                    if shallow_hierarchy is True:
                        self._add_dicom_attributes_to_hdf5_group(
                            patient_image_data,
                            data_set,
                            tags_to_use_as_attributes
                        )
                        if add_sitk_image_metadata_as_attributes:
                            self._add_sitk_image_attributes_to_hdf5_group(patient_image_data, data_set)

                    if patient_image_data.segmentations:
                        for segmentation_idx, segmentation in enumerate(patient_image_data.segmentations):
                            segmentation_group = series_group.create_group(name=str(segmentation_idx))
                            segmentation_group.attrs.create(name=self.MODALITY, data=segmentation.modality)

                            for organ, simple_itk_label_map in segmentation.simple_itk_label_maps.items():
                                if transpose is True:
                                    numpy_array_label_map = self._transpose(
                                        sitk.GetArrayFromImage(simple_itk_label_map)
                                    )
                                else:
                                    numpy_array_label_map = sitk.GetArrayFromImage(simple_itk_label_map)

                                if organs_to_keep is None or organ in organs_to_keep:
                                    segmentation_group.create_dataset(
                                        name=organ,
                                        data=numpy_array_label_map,
                                        dtype=np.int8
                                    )

                for idx, transform in enumerate(patient_dataset.transforms_history.history):
                    if shallow_hierarchy is True:
                        data_set.attrs.create(
                            name=f"{self.TRANSFORMS}_{idx}",
                            data=json.dumps(
                            obj=transform,
                            default=patient_dataset.transforms_history.serialize
                            )
                        )
                    else:
                        patient_group.attrs.create(
                            name=f"{self.TRANSFORMS}_{idx}",
                            data=json.dumps(
                                obj=transform,
                                default=patient_dataset.transforms_history.serialize
                            )
                        )

                _logger.info(f"Progress : {patient_idx + 1}/{number_of_patients} patients added to database.")

            patients_data_extractor.close()
            patients_data_extractor.reset()

        try:
            self._file = h5py.File(self.path_to_database, mode="r+")
        except OSError:
            self._file = h5py.File(self.path_to_database, mode="r")

        return patients_data_extractor.patients_who_failed

    def close(self):
        """
        Closes the hdf5 file database.
        """
        if self._file:
            self._file.close()

    def __del__(self):
        """
        Closes the hdf5 file database.
        """
        self.close()
