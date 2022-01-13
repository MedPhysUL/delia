import logging
from .logging_tools import logs_file_setup

from .settings import *

from .datasets.patient_dataset import PatientDataset
from .paths_manager.path_generator import PathGenerator

if __name__ == "__main__":
    # ----------------------------------------------------------------------------------------------------------- #
    #                                          Logs Setup                                                         #
    # ----------------------------------------------------------------------------------------------------------- #
    logs_file_setup(logging.INFO)

    # ----------------------------------------------------------------------------------------------------------- #
    #                                             Path Generator                                                  #
    # ----------------------------------------------------------------------------------------------------------- #
    path_generator = PathGenerator(
        path_to_patients_folder=PathName.PATH_TO_PATIENTS_FOLDER,
        path_to_segmentations_folder=PathName.PATH_TO_SEGMENTATIONS_FOLDER,
        images_folder_name=FolderName.IMAGES_FOLDER,
        verbose=True,
        patient_number_prefix="Ano"
    )

    # ----------------------------------------------------------------------------------------------------------- #
    #                                            Patient Dataset                                                  #
    # ----------------------------------------------------------------------------------------------------------- #
    dataset = PatientDataset(
        path_to_dataset=PathName.PATH_TO_PATIENT_DATASET,
    )

    dataset.create_hdf5_dataset(
        path_generator=path_generator,
        series_descriptions=PathName.PATH_TO_SERIES_DESCRIPTIONS_JSON,
        organs=PathName.PATH_TO_ORGANS_JSON,
        verbose=True,
        overwrite_dataset=True
    )
