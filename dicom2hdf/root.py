import os

"""
This file essentially gives the same important folders and paths root names to all files.
"""

ROOT = os.path.abspath(os.path.dirname(__file__))


class DatasetName:
    PATIENT_DATASET_BASE_NAME = "patient_dataset"
    RADIOMICS_DATASET_BASE_NAME = "radiomics_dataset"


class FolderName:
    DATA_FOLDER_NAME = "data"
    PATIENTS_FOLDER_NAME = "Patients"
    SEGMENTATIONS_FOLDER_NAME = "Segmentations"
    IMAGES_FOLDER_NAME = "IMAGES"


class PathName:
    PATH_TO_DATA_FOLDER = os.path.join(ROOT, FolderName.DATA_FOLDER_NAME)
    PATH_TO_PATIENTS_FOLDER = os.path.join(PATH_TO_DATA_FOLDER, FolderName.PATIENTS_FOLDER_NAME)
    PATH_TO_SEGMENTATIONS_FOLDER = os.path.join(PATH_TO_DATA_FOLDER, FolderName.SEGMENTATIONS_FOLDER_NAME)

    PATH_TO_PATIENT_DATASET = os.path.join(PATH_TO_DATA_FOLDER, DatasetName.PATIENT_DATASET_BASE_NAME)
    BASE_PATH_TO_RADIOMICS_DATASET = os.path.join(
        PATH_TO_DATA_FOLDER,
        DatasetName.RADIOMICS_DATASET_BASE_NAME
    )
