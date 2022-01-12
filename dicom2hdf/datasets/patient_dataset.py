"""
    @file:              patient_dataset.py
    @Author:            Maxence Larose

    @Creation Date:     10/2021
    @Last modification: 01/2022

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
import time
from tqdm import tqdm
from typing import Dict, List, Optional, Union

from ..data_readers.patient_data.patient_data_reader import PatientDataReader
from ..data_generators.patient_data_generator import PatientDataGenerator
from .tools.segmentation_filename_patterns_matcher import SegmentationFilenamePatternsMatcher


class PatientDataset:
    """
    This file contains the PatientDataset class that is used to interact with an hdf5 file dataset. The main purpose of
    this class is to create an hdf5 file dataset from multiple patients dicom files and their segmentation. This class
    also allows the user to interact with an existing hdf5 file dataset through queries.
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
            self._path_to_dataset = f"{path_to_dataset}" + ".h5"

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
                logging.info(f"Overwriting dataset (HDF5 dataset file path : {self.path_to_dataset}).")
        else:
            logging.info(f"Writing dataset (HDF5 dataset file path : {self.path_to_dataset}).")

    @staticmethod
    def get_paths_to_patient(
            paths_to_patients_dicom_folder: List[str],
            path_to_segmentations_folder: str,
            patient_number_prefix: str = "Ano"
    ) -> List[PatientDataGenerator.PathsToPatientFolderAndSegmentations]:
        """
        Paths to patients dicom folder.

        Parameters
        ----------
        paths_to_patients_dicom_folder : List[str]
            List of the paths to all the patients dicom folder.
        path_to_segmentations_folder : str
            Path to the folder containing the segmentations.
        patient_number_prefix : str
            Prefix of the patient number common to all segmentations (default is 'Ano').
        """
        paths_to_patients_folder_and_segmentations = []

        for path_to_patient_dicom_folder in paths_to_patients_dicom_folder:
            patient_data_reader = PatientDataReader(
                path_to_dicom_folder=path_to_patient_dicom_folder,
                verbose=True,
            )

            segmentation_filename_patterns_matcher = SegmentationFilenamePatternsMatcher(
                path_to_segmentations_folder=path_to_segmentations_folder,
                patient_name=patient_data_reader.patient_name,
                patient_number_prefix=patient_number_prefix
            )

            paths_to_segmentations = segmentation_filename_patterns_matcher.get_absolute_paths_to_segmentation_files()

            paths_to_patient_folder_and_segmentations = PatientDataGenerator.PathsToPatientFolderAndSegmentations(
                path_to_patient_folder=path_to_patient_dicom_folder,
                path_to_segmentations=paths_to_segmentations
            )

            paths_to_patients_folder_and_segmentations.append(paths_to_patient_folder_and_segmentations)

        return paths_to_patients_folder_and_segmentations

    def create_hdf5_dataset(
            self,
            path_to_patients_folder: str,
            path_to_segmentations_folder: str,
            images_folder_name: str,
            verbose: bool,
            series_descriptions: Optional[Union[str, Dict[str, List[str]]]] = None,
            organs: Optional[Union[str, Dict[str, List[str]]]] = None,
            patient_number_prefix: str = "Ano",
            overwrite_dataset: bool = True,
    ) -> None:
        """
        Create an hdf5 file dataset from multiple patients dicom files and their segmentation and get patient's images
        from this dataset. The goal is to create an object from which it is easier to obtain patient images and their
        segmentation than separated dicom files and segmentation files.

        Parameters
        ----------
        path_to_patients_folder : str
            Patients folder path.
        path_to_segmentations_folder : str
            Images folder name.
        series_descriptions : Union[str, Dict[str, List[str]]]
            A dictionary that contains the series descriptions of the images that absolutely needs to be extracted from
            the patient's file. Keys are arbitrary names given to the images we want to add and values are lists of
            series descriptions. The images associated with these series descriptions do not need to have a
            corresponding segmentation. In fact, the whole point of adding a way to specify the series descriptions that
            must be added to the dataset is to be able to add images without their segmentation. Can be specified as a
            path to a json dictionary that contains the series descriptions.
        organs : Union[str, Dict[str, List[str]]]
            A dictionary that contains the organs and their associated segment names. Keys are arbitrary organ names
            and values are lists of possible segment names. It can also be specified as a path to a json file that
            contains the organs dictionary.
        images_folder_name : str
            Images folder name.
        verbose : bool
            True to log/print some information else False.
        patient_number_prefix : str
            Prefix of the patient number common to all segmentations (default is 'Ano').
        overwrite_dataset : bool, default = False.
            Overwrite existing dataset.
        """
        self._check_authorization_of_dataset_creation(overwrite_dataset=overwrite_dataset)

        hf = h5py.File(self.path_to_dataset, "w")

        paths_to_patients_dicom_folder = []
        for path_to_patient_folder in os.listdir(path_to_patients_folder):
            path_to_dicom_folder = os.path.join(
                path_to_patients_folder,
                path_to_patient_folder,
                images_folder_name
            )
            paths_to_patients_dicom_folder.append(path_to_dicom_folder)

        if verbose:
            logging.info("\nAssociating patient records with their corresponding image segmentation files...")
        paths_to_patients_folder_and_segmentations = self.get_paths_to_patient(
            paths_to_patients_dicom_folder=paths_to_patients_dicom_folder,
            path_to_segmentations_folder=path_to_segmentations_folder,
            patient_number_prefix=patient_number_prefix
        )

        if verbose:
            logging.info("Done.")

        patient_data_generator = PatientDataGenerator(
            paths_to_patients_folder_and_segmentations=paths_to_patients_folder_and_segmentations,
            verbose=verbose,
            series_descriptions=series_descriptions,
            organs=organs
        )

        if verbose:
            print("\nProgress:")
            time.sleep(0.001)
            progress_bar = tqdm(range(len(patient_data_generator)), unit='itr', postfix="patients")
            time.sleep(0.001)
        for patient_dataset in patient_data_generator:
            patient_name = patient_dataset.patient_name
            patient_group = hf.create_group(name=patient_name)

            for idx, patient_image_data in enumerate(patient_dataset.data):
                series_description = patient_image_data.image.dicom_header.SeriesDescription
                series_uid = patient_image_data.image.dicom_header.SeriesInstanceUID
                modality = patient_image_data.image.dicom_header.Modality

                image_array = sitk.GetArrayFromImage(patient_image_data.image.simple_itk_image)
                transposed_image_array = image_array.transpose(1, 2, 0)

                series_group = patient_group.create_group(name=str(idx))
                series_group.attrs.__setitem__(name="series_description", value=series_description)
                series_group.attrs.__setitem__(name="series_uid", value=str(series_uid))
                series_group.attrs.__setitem__(name="modality", value=modality)

                series_group.create_dataset(
                    name=f"image",
                    data=transposed_image_array
                )

                series_group.create_dataset(
                    name=f"dicom_header",
                    data=json.dumps(patient_image_data.image.dicom_header.to_json_dict())
                )

                if patient_image_data.segmentation is None:
                    pass
                else:
                    for organ, label_map in patient_image_data.segmentation.binary_label_maps.items():
                        series_group.create_dataset(
                            name=f"{organ}_label_map",
                            data=label_map
                        )

            if verbose:
                print("\nProgress:")
                time.sleep(0.001)
                progress_bar.update()
                time.sleep(0.001)

        if verbose:
            progress_bar.close()

        patient_data_generator.close()
