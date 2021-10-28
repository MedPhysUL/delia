import logging
from logging_tools import logs_file_setup

from root import *

from src.datasets.patient_dataset import PatientDataset


if __name__ == "__main__":
    # ----------------------------------------------------------------------------------------------------------- #
    #                                          Logs Setup                                                         #
    # ----------------------------------------------------------------------------------------------------------- #
    logs_file_setup(__file__, logging.INFO)

    # ----------------------------------------------------------------------------------------------------------- #
    #                                            Patient Dataset                                                  #
    # ----------------------------------------------------------------------------------------------------------- #
    hdf5_dataset = PatientDataset(
        base_path_to_dataset=PathName.PATH_TO_PATIENT_DATASET,
    )

    hdf5_dataset.create_dataset_from_dicom_and_segmentation_files(
        path_to_patients_folder=PathName.PATH_TO_PATIENTS_FOLDER,
        path_to_segmentations_folder=PathName.PATH_TO_SEGMENTATIONS_FOLDER,
        path_to_series_description_json=os.path.join(PathName.PATH_TO_DATA_FOLDER, "series_descriptions.json"),
        images_folder_name=FolderName.IMAGES_FOLDER_NAME,
        overwrite_dataset=True
    )
