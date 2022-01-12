import os

"""
This file essentially gives the same important folders and paths root names to all files.
"""

ROOT = os.path.abspath(os.path.dirname(__file__))


class FileName:
    ORGANS_JSON = "organs.json"
    SERIES_DESCRIPTIONS_JSON = "series_descriptions.json"
    PATIENT_DATASET = "patient_dataset.h5"


class FolderName:
    DATA_FOLDER = "data"
    PATIENTS_FOLDER = "Patients"
    SEGMENTATIONS_FOLDER = "Segmentations"
    IMAGES_FOLDER = "IMAGES"


class PathName:
    PATH_TO_DATA_FOLDER = os.path.join(ROOT, FolderName.DATA_FOLDER)

    PATH_TO_ORGANS_JSON = os.path.join(PATH_TO_DATA_FOLDER, FileName.ORGANS_JSON)
    PATH_TO_SERIES_DESCRIPTIONS_JSON = os.path.join(PATH_TO_DATA_FOLDER, FileName.SERIES_DESCRIPTIONS_JSON)
    PATH_TO_PATIENT_DATASET = os.path.join(PATH_TO_DATA_FOLDER, FileName.PATIENT_DATASET)

    PATH_TO_PATIENTS_FOLDER = os.path.join(PATH_TO_DATA_FOLDER, FolderName.PATIENTS_FOLDER)
    PATH_TO_SEGMENTATIONS_FOLDER = os.path.join(PATH_TO_DATA_FOLDER, FolderName.SEGMENTATIONS_FOLDER)
