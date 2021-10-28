import os
import logging

import glob
import h5py
import json
import pydicom
import SimpleITK as sitk
from typing import List, Tuple, Union

from src.data_readers.patient_data_generator import PatientDataGenerator
from .segmentation_filename_patterns_matcher import SegmentationFilenamePatternsMatcher
from src.data_readers.dicom_reader import DicomReader
from src.constants.segmentation_category import SegmentationCategory

# TODO : Add ways to navigate through the dataset


class PatientDataset(object):

    def __init__(
            self,
            base_path_to_dataset: str,
    ):
        """
        This class allows the user to query an hdf5 dataset saved in an hdf5 file.

        Parameters
        ----------
        base_path_to_dataset : str
            Path to dataset.
        segmentation_category : SegmentationCategory
            Segmentation category.
        """
        self.base_path_to_dataset = base_path_to_dataset

    @property
    def path_to_dataset(self) -> str:
        """
        Path to dataset.

        Returns
        -------
        path_to_dataset : str
            Path to dataset containing modality and organ names.
        """
        path = f"{self.base_path_to_dataset}" + ".h5"

        return path

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
                logging.info(f"Overwriting dataset with path : {self.path_to_dataset}.")
        else:
            logging.info(f"Writing dataset with path : {self.path_to_dataset}.")

    def get_paths_to_patient(
            self,
            paths_to_patient_dicom_folder: List[str],
            path_to_segmentations_folder: str
    ) -> List[Tuple[str, Union[List[str], None]]]:

        paths_to_patients_folder_and_segmentations = []

        for path_to_patient_dicom_folder in paths_to_patient_dicom_folder:
            first_dicom = os.path.join(path_to_patient_dicom_folder, os.listdir(path_to_patient_dicom_folder)[0])
            dicom_reader = DicomReader()
            dicom_header = dicom_reader._get_dicom_header(path_to_dicom=first_dicom)
            patient_name = str(dicom_header.PatientName)

            segmentation_filename_patterns_matcher = SegmentationFilenamePatternsMatcher(
                path_to_segmentations_folder=path_to_segmentations_folder,
                patient_name=patient_name
            )

            paths_to_segmentations = segmentation_filename_patterns_matcher.get_absolute_path_to_segmentation_file()

            paths_to_patients_folder_and_segmentations.append((path_to_patient_dicom_folder, paths_to_segmentations))

        return paths_to_patients_folder_and_segmentations

    def create_dataset_from_dicom_and_segmentation_files(
            self,
            path_to_patients_folder: str,
            path_to_segmentations_folder: str,
            path_to_series_description_json: str,
            images_folder_name: str,
            overwrite_dataset: bool = True,
    ) -> None:
        """
        Create an hdf5 file dataset from multiple patients dicom files and their segmentation and get patient's images
        from this dataset. The goal is to create an object from which it is easier to obtain patient images and their
        segmentation than separated dicom files and segmentation nrrd files.

        Parameters
        ----------
        path_to_patients_folder : str
            Patients folder path.
        path_to_segmentations_folder : str
            Images folder name.
        images_folder_name : str
            Images folder name.
        overwrite_dataset : bool, default = False.
            Overwrite existing dataset.
        """
        self._check_authorization_of_dataset_creation(overwrite_dataset=overwrite_dataset)

        hf = h5py.File(self.path_to_dataset, "w")

        paths_to_patient_dicom_folder = []
        for path_to_patient_folder in os.listdir(path_to_patients_folder):
            path_to_dicom_folder = os.path.join(
                path_to_patients_folder,
                path_to_patient_folder,
                images_folder_name
            )
            paths_to_patient_dicom_folder.append(path_to_dicom_folder)

        paths_to_patients_folder_and_segmentations = self.get_paths_to_patient(
            paths_to_patient_dicom_folder=paths_to_patient_dicom_folder,
            path_to_segmentations_folder=path_to_segmentations_folder
        )

        patient_data_generator = PatientDataGenerator(
            paths_to_patients_folder_and_segmentations=paths_to_patients_folder_and_segmentations,
            path_to_series_description_json=path_to_series_description_json
        )

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
                    segmentation_metadata = patient_image_data.segmentation.metadata
                    segmentation_metadata_dict = dict((k, val._asdict()) for k, val in segmentation_metadata.items())
                    series_group.create_dataset(
                        name=f"segmentation_metadata",
                        data=json.dumps(segmentation_metadata_dict)
                    )

        patient_data_generator.save_series_descriptions_to_json()
