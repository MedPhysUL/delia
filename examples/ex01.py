import env_examples  # Modifies path, DO NOT REMOVE

from datetime import datetime
import logging.config
import os
import yaml

from dicom2hdf import PatientDataset
from settings import FolderName, PathName


# def configure_logging(path_to_configuration_file: str):
#     now = datetime.now()
#     logs_dir = f"logs/{now.strftime('%Y-%m-%d')}"
#     logs_file = f"{logs_dir}/{now.strftime('%Y-%m-%d_%H-%M-%S')}.log"
#     os.makedirs(logs_dir, exist_ok=True)
#
#     with open(path_to_configuration_file, 'r') as stream:
#         config: dict = yaml.load(stream, Loader=yaml.FullLoader)
#
#     config["handlers"]["file"]["filename"] = logs_file
#
#     logging.config.dictConfig(config)


if __name__ == "__main__":
    # ----------------------------------------------------------------------------------------------------------- #
    #                                              Logs Setup                                                     #
    # ----------------------------------------------------------------------------------------------------------- #
    # configure_logging("logging_conf.yaml")

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
        overwrite_dataset=True
    )
