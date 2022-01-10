import logging
from logging_tools import logs_file_setup
import warnings

from root import *

from src.datasets.patient_dataset import PatientDataset


if __name__ == "__main__":
    # ----------------------------------------------------------------------------------------------------------- #
    #                                          Logs Setup                                                         #
    # ----------------------------------------------------------------------------------------------------------- #
    logs_file_setup(__file__, logging.INFO)
    warnings.filterwarnings("default", category=DeprecationWarning)

    # ----------------------------------------------------------------------------------------------------------- #
    #                                            Patient Dataset                                                  #
    # ----------------------------------------------------------------------------------------------------------- #
    hdf5_dataset = PatientDataset(
        path_to_dataset=PathName.PATH_TO_PATIENT_DATASET,
    )

    hdf5_dataset.create_hdf5_dataset(
        path_to_patients_folder=PathName.PATH_TO_PATIENTS_FOLDER,
        path_to_segmentations_folder=PathName.PATH_TO_SEGMENTATIONS_FOLDER,
        series_descriptions=os.path.join(PathName.PATH_TO_DATA_FOLDER, "series_descriptions.json"),
        organs=os.path.join(PathName.PATH_TO_DATA_FOLDER, "organs.json"),
        images_folder_name=FolderName.IMAGES_FOLDER_NAME,
        verbose=True,
        overwrite_dataset=True
    )
