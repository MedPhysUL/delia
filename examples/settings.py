"""
    @file:              settings.py
    @Author:            Maxence Larose

    @Creation Date:     10/2021
    @Last modification: 01/2022

    @Description:       Stores custom enumerations of the important file names, folder names and paths within the
                        project.
"""

from os.path import abspath, dirname, join

ROOT = abspath(dirname(__file__))


class FileName:
    SERIES_DESCRIPTIONS_JSON: str = "series_descriptions.json"
    PATIENT_DATASET_HDF5: str = "patient_dataset.h5"


class FolderName:
    DATA_FOLDER: str = "data"
    PATIENTS_FOLDER: str = "Patients_WORKING"
    IMAGES_FOLDER: str = "images"
    SEGMENTATIONS_FOLDER: str = "segmentations"


class PathName:
    PATH_TO_DATA_FOLDER: str = join(ROOT, FolderName.DATA_FOLDER)

    PATH_TO_SERIES_DESCRIPTIONS_JSON: str = join(PATH_TO_DATA_FOLDER, FileName.SERIES_DESCRIPTIONS_JSON)
    PATH_TO_PATIENT_DATASET_HDF5: str = join(PATH_TO_DATA_FOLDER, FileName.PATIENT_DATASET_HDF5)

    PATH_TO_PATIENTS_FOLDER: str = join(PATH_TO_DATA_FOLDER, FolderName.PATIENTS_FOLDER)
