import logging
from .logging_tools import logs_file_setup

from .settings import *

from .datasets.patient_dataset import PatientDataset

if __name__ == "__main__":
    # ----------------------------------------------------------------------------------------------------------- #
    #                                          Logs Setup                                                         #
    # ----------------------------------------------------------------------------------------------------------- #
    logs_file_setup(logging.INFO)

    # ----------------------------------------------------------------------------------------------------------- #
    #                                            Patient Dataset                                                  #
    # ----------------------------------------------------------------------------------------------------------- #
    dataset = PatientDataset(
        path_to_dataset=PathName.PATH_TO_PATIENT_DATASET_HDF5,
    )

    dataset.create_hdf5_dataset(
        path_to_patients_folder=PathName.PATH_TO_PATIENTS_FOLDER,
        images_folder_name=FolderName.IMAGES_FOLDER,
        segmentations_folder_name=FolderName.SEGMENTATIONS_FOLDER,
        series_descriptions=PathName.PATH_TO_SERIES_DESCRIPTIONS_JSON,
        verbose=True,
        overwrite_dataset=True
    )
