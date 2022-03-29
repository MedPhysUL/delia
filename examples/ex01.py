import env_examples  # Modifies path, DO NOT REMOVE

from dicom2hdf import PatientDataset
from logging_tools import configure_logging


if __name__ == "__main__":
    # ----------------------------------------------------------------------------------------------------------- #
    #                                         Logs Setup (Optional)                                               #
    # ----------------------------------------------------------------------------------------------------------- #
    configure_logging("logging_conf.yaml")

    # ----------------------------------------------------------------------------------------------------------- #
    #                                            Patient Dataset                                                  #
    # ----------------------------------------------------------------------------------------------------------- #
    dataset = PatientDataset(
        path_to_dataset="data/patient_dataset.h5",
    )

    dataset.create_hdf5_dataset(
        path_to_patients_folder="data/Patients_WORKING",
        images_folder_name="images",
        segmentations_folder_name="segmentations",
        series_descriptions="data/series_descriptions.json",
        overwrite_dataset=True
    )
