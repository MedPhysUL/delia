"""
    @Title:             Logging + database creation.

    @Description:       Configure logging and create database.
"""

import env_examples  # Modifies path, DO NOT REMOVE

from dicom2hdf import PatientsDatabase
from dicom2hdf import transforms


if __name__ == "__main__":
    # ----------------------------------------------------------------------------------------------------------- #
    #                                         Logs Setup (Optional)                                               #
    # ----------------------------------------------------------------------------------------------------------- #
    env_examples.configure_logging("logging_conf.yaml")

    # ----------------------------------------------------------------------------------------------------------- #
    #     Create database (some images of some patients might fail to be added to the database due to the         #
    #                         absence of the series descriptions in the patient record)                           #
    # ----------------------------------------------------------------------------------------------------------- #
    database = PatientsDatabase(
        path_to_database="data/patients_database.h5",
    )

    patients_who_failed = database.create(
        path_to_patients_folder="data/Patients",
        tags_to_use_as_attributes=[(0x0008, 0x103E), (0x0020, 0x000E), (0x0008, 0x0060)],
        series_descriptions="data/series_descriptions.json",
        transforms=[transforms.Resample()],
        overwrite_database=True
    )

    # Print list of patients who failed
    print(f"Patients who failed the pipeline : {patients_who_failed}")
