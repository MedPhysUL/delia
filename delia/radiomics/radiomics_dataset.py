"""
    @file:              radiomics_dataset.py
    @Author:            Maxence Larose

    @Creation Date:     11/2022
    @Last modification: 11/2022

    @Description:       This file contains the RadiomicsDataset class which is used to create a dataset containing
                        radiomics information about images and segmentations.
"""

import logging
import os
from typing import Dict, List, Optional

import pandas as pd
from radiomics.featureextractor import RadiomicsFeatureExtractor

from delia.extractors import PatientsDataExtractor
from delia.readers.segmentation.segmentation_strategy import SegmentationStrategies

_logger = logging.getLogger(__name__)


class RadiomicsDataset:

    DEFAULT_INDEX_LABEL = "ID"

    def __init__(
            self,
            path_to_dataset: str
    ):
        """
        Used to interact with a dataset of radiomics features.

        Parameters
        ----------
        path_to_dataset : str
            Path to dataset.
        """
        self.path_to_dataset = path_to_dataset
        self._extractor = None

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
        Sets path to dataset.

        Parameters
        ----------
        path_to_dataset : str
            Path to dataset.
        """
        if path_to_dataset.endswith(".csv"):
            self._path_to_dataset = path_to_dataset
        else:
            self._path_to_dataset = f"{path_to_dataset}.csv"

    @property
    def extractor(self) -> Optional[RadiomicsFeatureExtractor]:
        """
        Radiomics extractor.

        Returns
        -------
        extractor : RadiomicsFeatureExtractor
            Radiomics extractor.
        """
        return self._extractor

    @extractor.setter
    def extractor(self, extractor: RadiomicsFeatureExtractor) -> None:
        """
        Set radiomics extractor.

        Parameters
        ----------
        extractor : RadiomicsFeatureExtractor
            Radiomics extractor.
        """
        self._extractor = extractor

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
                raise FileExistsError(
                    "The dataset already exists. You may overwrite it using overwrite_dataset = True."
                )
            else:
                _logger.info(f"Overwriting dataset with path : {self.path_to_dataset}.")
        else:
            _logger.info(f"Writing dataset with path : {self.path_to_dataset}.")

    @staticmethod
    def convert_list_of_dicts_to_dict_of_lists(list_of_dicts: List[Dict]) -> Dict[str, List]:
        """
        Converts a list of dictionaries into a dictionary of lists.

        Parameters
        ----------
        list_of_dicts : List[Dict]
            List of dictionaries. Example : [{"a": 1, "b": 2}, {"a": 3, "b": 4}].

        Returns
        -------
        dict_of_lists : Dict[str, List]
            Dictionary of lists. Example : {"a": [1, 3], "b": [2, 4]}.
        """
        dict_of_lists = {k: [dic[k] for dic in list_of_dicts] for k in list_of_dicts[0]}

        return dict_of_lists

    @staticmethod
    def convert_dict_of_lists_to_list_of_dicts(dict_of_lists: Dict[str, List]) -> List[Dict]:
        """
        Converts a dictionary of lists into a list of dictionaries.

        Parameters
        ----------
        dict_of_lists : Dict[str, List]
            Dictionary of lists. Example : {"a": [1, 3], "b": [2, 4]}.

        Returns
        -------
        dict_of_lists : Dict[str, List]
            List of dictionaries. Example : [{"a": 1, "b": 2}, {"a": 3, "b": 4}].
        """
        list_of_dicts = [dict(zip(dict_of_lists, t)) for t in zip(*dict_of_lists.values())]

        return list_of_dicts

    def create(
            self,
            patients_data_extractor: PatientsDataExtractor,
            organ: str,
            image_name: Optional[str] = None,
            image_modality: Optional[str] = None,
            segmentation_modality_to_prioritize: str = "SEG",
            overwrite_dataset: bool = False,
            **kwargs
    ) -> None:
        """
        Create radiomics datasets from all patients data.

        Parameters
        ----------
        patients_data_extractor : PatientsDataExtractor
            An object used to iterate on multiple patients' dicom files and segmentation files using the
            PatientDataReader to obtain all patients' data.
        organ : str
            The organ specifies the segment of the mask from which the radiomics features are to be acquired.
        image_name : Optional[str]
            Arbitrary name given to the image in the 'tag_values' dictionary. If 'tag_values' is
            None, use 'image_modality'.
        image_modality : Optional[str]
            Image modality. If 'tag_values' is NOT None, use 'image_name'.
        segmentation_modality_to_prioritize : str
            If there is multiple segmentation of the same organ for the same patient, this parameter sets the modality
            of the segmentation to prioritize, i.e. "SEG" or "RTSTRUCT". Default = "SEG".
        overwrite_dataset : bool
            Overwrite existing dataset, default = False.
        kwargs : {
            geometry_tolerance : float
                Image/Mask geometry mismatch tolerance.
            label : int, default = 1
                Integer, value of the label for which to extract features. If not specified, last specified label is
                used.
            label_channel : int, default = 0
                Integer, index of the channel to use when maskFilepath yields a SimpleITK.Image with a vector pixel
                type.
            voxel_based : bool, default = False
                If set to true, a voxel-based extraction is performed, segment-based otherwise.
        }
        """
        if not image_name and not image_modality:
            raise AssertionError(
                f"Parameters 'image_name' or 'image_modality' must be provided. Found 'image_name'={image_name} and "
                f"'image_modality'={image_modality}."
            )
        elif image_name and image_modality:
            raise AssertionError(
                f"Parameters 'image_name' OR 'image_modality' must be provided. Both are provided. Found "
                f"'image_name'={image_name} and 'image_modality'={image_modality}. One of the two must be None."
            )

        if segmentation_modality_to_prioritize not in SegmentationStrategies.get_available_modalities():
            raise AssertionError(
                f"Unknown 'segmentation_modality_to_prioritize={segmentation_modality_to_prioritize}'. Available "
                f"modalities are {SegmentationStrategies.get_available_modalities()}."
            )
        if not self.extractor:
            raise AssertionError("The 'extractor' needs to be set before creating the radiomics dataset.")

        self._check_authorization_of_dataset_creation(overwrite_dataset=overwrite_dataset)

        radiomics_features: Dict[str, dict] = {}
        for patient_idx, patient_dataset in enumerate(patients_data_extractor):
            image, mask = None, None
            for image_idx, patient_image_data in enumerate(patient_dataset.data):
                series_key = patient_image_data.image.series_key
                modality = patient_image_data.image.dicom_header.Modality

                if image_name:
                    if series_key == image_name:
                        image = patient_image_data.image.simple_itk_image
                elif image_modality:
                    if modality == image_modality:
                        image = patient_image_data.image.simple_itk_image

                if image:
                    if patient_image_data.segmentations:
                        available_modalities = []
                        for seg in patient_image_data.segmentations:
                            if organ in seg.simple_itk_label_maps.keys():
                                available_modalities.append(seg.modality)
                        if segmentation_modality_to_prioritize in available_modalities:
                            seg_idx = available_modalities.index(segmentation_modality_to_prioritize)
                        else:
                            seg_idx = 0

                        segmentation = patient_image_data.segmentations[seg_idx]
                        for _organ, _mask in segmentation.simple_itk_label_maps.items():
                            if _organ == organ:
                                mask = _mask
                    break

            if not image:
                if image_name:
                    _logger.warning(f"No image found with name {image_name} for patient {patient_id}.")
                elif image_modality:
                    _logger.warning(f"No image found with modality {image_modality} for patient {patient_id}.")
            if not mask:
                _logger.warning(f"No mask found for organ {organ} for patient {patient_id}.")

            if image and mask:
                radiomics = self.extractor.execute(
                    imageFilepath=image,
                    maskFilepath=mask,
                    label=kwargs.get("label", None),
                    label_channel=kwargs.get("label_channel", None),
                    voxelBased=kwargs.get("voxel_based", False)
                )

                radiomics_features[patient_dataset.patient_id] = radiomics

        if radiomics_features:
            self.save(radiomics_features=radiomics_features)
        else:
            _logger.error(
                f"No images found for all patients. The radiomics dataset with path {self.path_to_dataset} was "
                f"therefore not created."
            )

        patients_data_extractor.reset()
        patients_data_extractor.close()

    def read(self) -> pd.DataFrame:
        """
        Read dataset.

        Returns
        -------
        dataframe : pd.DataFrame
            Radiomics pandas dataframe.
        """
        dataframe = pd.read_csv(filepath_or_buffer=self.path_to_dataset, index_col=self.DEFAULT_INDEX_LABEL)

        return dataframe

    def save(
            self,
            radiomics_features: Dict[str, dict]
    ) -> None:
        """
        Save radiomics features to dataset. The dataset is overwritten.

        Parameters
        ----------
        radiomics_features : Dict[str, dict]
            Radiomics features of multiple patients. The keys are the patient IDs, the values are the radiomics features
            of the corresponding patient. The radiomics features are stored in a dictionary, where the keys are the
            feature names and the values are the feature values.
        """
        radiomics_features_of_multiple_patients = self.convert_list_of_dicts_to_dict_of_lists(
            list_of_dicts=list(radiomics_features.values())
        )

        dataframe = pd.DataFrame(
            data=radiomics_features_of_multiple_patients,
            index=list(radiomics_features.keys())
        )

        dataframe.to_csv(
            path_or_buf=self.path_to_dataset,
            sep=",",
            index=True,
            index_label=self.DEFAULT_INDEX_LABEL
        )
