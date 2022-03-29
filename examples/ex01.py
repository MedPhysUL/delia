"""
    @Title:             Logging + dataset creation.

    @Description:       Configure logging and create dataset.
"""

import env_examples  # Modifies path, DO NOT REMOVE

from dicom2hdf import PatientDataset


if __name__ == "__main__":
    # ----------------------------------------------------------------------------------------------------------- #
    #                                         Logs Setup (Optional)                                               #
    # ----------------------------------------------------------------------------------------------------------- #
    env_examples.configure_logging("logging_conf.yaml")

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
        tags_to_use_as_attributes=[(0x0008, 0x103E), (0x0020, 0x000E), (0x0008, 0x0060)],
        series_descriptions="data/series_descriptions.json",
        overwrite_dataset=True
    )

    # Print list of patients who failed
    print(f"Patients who failed the pipeline : {patients_who_failed}")
