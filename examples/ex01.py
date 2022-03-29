"""
    @Title:             Logging + dataset creation.

    @Description:       Configure logging and create dataset.
"""

import env_examples  # Modifies path, DO NOT REMOVE

from dicom2hdf import PatientDataset
from logging_tools import configure_logging


if __name__ == "__main__":
    # ----------------------------------------------------------------------------------------------------------- #
    #                                         Logs Setup (Optional)                                               #
    # ----------------------------------------------------------------------------------------------------------- #
    configure_logging("logging_conf.yaml")

    # ----------------------------------------------------------------------------------------------------------- #
    #            Create dataset (some images of some patients might fail to be added to the dataset)              #
    # ----------------------------------------------------------------------------------------------------------- #
    dataset = PatientDataset(
        path_to_dataset="data/patient_dataset.h5",
    )

    patients_who_failed = dataset.create_hdf5_dataset(
        path_to_patients_folder="data/patients",
        images_folder_name="images",
        segmentations_folder_name="segmentations",
        series_descriptions="data/series_descriptions.json",
        overwrite_dataset=True
    )

    # Print list of patients who failed
    print(f"Patients who failed the pipeline : {patients_who_failed}")
