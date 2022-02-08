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

from ..data_generators.patient_data_generator import PatientDataGenerator


class PatientDataset:
    """
    A class that is used to interact with a patient dataset. The main purpose of this class is to create an hdf5 file
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

    def create_hdf5_dataset(
            self,
            path_to_patients_folder: str,
            images_folder_name: str = "images",
            segmentations_folder_name: str = "segmentations",
            series_descriptions: Optional[Union[str, Dict[str, List[str]]]] = None,
            verbose: bool = True,
            overwrite_dataset: bool = False,
    ) -> None:
        """
        Create an hdf5 file dataset from multiple patients dicom files and their segmentation and get patient's images
        from this dataset. The goal is to create an object from which it is easier to obtain patient images and their
        segmentation than separated dicom files and segmentation files.

        Parameters
        ----------
        path_to_patients_folder : str
            The path to the folder that contains all the patients' folders.
        images_folder_name : str, default = "images".
            Images folder name.
        segmentations_folder_name : str, default = "segmentations".
            Segmentations folder name.
        series_descriptions : Union[str, Dict[str, List[str]]], default = None.
            A dictionary that contains the series descriptions of the images that absolutely needs to be extracted from
            the patient's file. Keys are arbitrary names given to the images we want to add and values are lists of
            series descriptions. The images associated with these series descriptions do not need to have a
            corresponding segmentation. In fact, the whole point of adding a way to specify the series descriptions that
            must be added to the dataset is to be able to add images without their segmentation. Can be specified as a
            path to a json dictionary that contains the series descriptions.
        verbose : bool, default = True.
            True to log/print some information else False.
        overwrite_dataset : bool, default = False.
            Overwrite existing dataset.
        """
        self._check_authorization_of_dataset_creation(overwrite_dataset=overwrite_dataset)

        hf = h5py.File(self.path_to_dataset, "w")

        patient_data_generator = PatientDataGenerator(
            path_to_patients_folder=path_to_patients_folder,
            images_folder_name=images_folder_name,
            segmentations_folder_name=segmentations_folder_name,
            verbose=verbose,
            series_descriptions=series_descriptions,
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
                    for organ, simple_itk_label_map in patient_image_data.segmentation.simple_itk_label_maps.items():
                        numpy_array_label_map = sitk.GetArrayFromImage(simple_itk_label_map)
                        transposed_numpy_array_label_map = numpy_array_label_map.transpose(1, 2, 0)
                        series_group.create_dataset(
                            name=f"{organ}_label_map",
                            data=transposed_numpy_array_label_map
                        )

            if verbose:
                print("\nProgress:")
                time.sleep(0.001)
                progress_bar.update()
                time.sleep(0.001)

        if verbose:
            progress_bar.close()

        patient_data_generator.close()
