import os
from dataclasses import dataclass

"""
This file essentially gives the same important folders and paths root names to all files.
"""


@dataclass
class DatasetName:
    PATIENT_DATASET_BASE_NAME = "patient_dataset"
    RADIOMICS_DATASET_BASE_NAME: str = "radiomics_dataset"


@dataclass
class FolderName:
    DATA_FOLDER_NAME: str = "data"
    PATIENTS_FOLDER_NAME: str = "Patients"
    SEGMENTATIONS_FOLDER_NAME: str = "Segmentations"
    IMAGES_FOLDER_NAME: str = "IMAGES"


@dataclass
class PathName:
    ROOT: str = os.path.abspath(os.path.dirname(__file__))

    PATH_TO_DATA_FOLDER: str = os.path.join(ROOT, FolderName.DATA_FOLDER_NAME)
    PATH_TO_PATIENTS_FOLDER: str = os.path.join(PATH_TO_DATA_FOLDER, FolderName.PATIENTS_FOLDER_NAME)
    PATH_TO_SEGMENTATIONS_FOLDER: str = os.path.join(PATH_TO_DATA_FOLDER, FolderName.SEGMENTATIONS_FOLDER_NAME)

    PATH_TO_PATIENT_DATASET: str = os.path.join(PATH_TO_DATA_FOLDER, DatasetName.PATIENT_DATASET_BASE_NAME)
    BASE_PATH_TO_RADIOMICS_DATASET: str = os.path.join(PATH_TO_DATA_FOLDER, DatasetName.RADIOMICS_DATASET_BASE_NAME)
