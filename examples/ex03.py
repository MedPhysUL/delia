"""
    @Title:             Logging + database creation.

    @Description:       Configure logging and create database.
"""

import env_examples  # Modifies path, DO NOT REMOVE

from delia.databases import PatientsDatabase
from delia.extractors import PatientsDataExtractor
from delia.transforms import (
    MatchingResampleD,
    PETtoSUVD,
    ResampleD
)
from monai.transforms import (
    CenterSpatialCropD,
    Compose,
    ScaleIntensityRangeD
)


if __name__ == "__main__":
    # ----------------------------------------------------------------------------------------------------------- #
    #                                         Logs Setup (Optional)                                               #
    # ----------------------------------------------------------------------------------------------------------- #
    env_examples.configure_logging("logging_conf.yaml")

    # ----------------------------------------------------------------------------------------------------------- #
    #                                      Create patients data extractor                                         #
    # ----------------------------------------------------------------------------------------------------------- #
    patients_data_extractor = PatientsDataExtractor(
        path_to_patients_folder="data/patients",
        series_descriptions="data/series_descriptions.json",
        transforms=Compose(
            [
                ResampleD(keys=["CT_THORAX", "PET", "Heart"], out_spacing=(1.5, 1.5, 1.5)),
                MatchingResampleD(reference_image_key="CT_THORAX", matching_keys=["PET", "Heart"]),
                CenterSpatialCropD(keys=["CT_THORAX", "PET", "Heart"], roi_size=(1000, 160, 160)),
                ScaleIntensityRangeD(keys=["CT_THORAX"], a_min=-250, a_max=500, b_min=0, b_max=1, clip=True),
                PETtoSUVD(keys=["PET"])
            ]
        )
    )

    # ----------------------------------------------------------------------------------------------------------- #
    #                                                Create database                                              #
    # ----------------------------------------------------------------------------------------------------------- #
    database = PatientsDatabase(path_to_database="data/patients_database.h5")

    database.create(
        patients_data_extractor=patients_data_extractor,
        tags_to_use_as_attributes=[(0x0008, 0x103E), (0x0020, 0x000E), (0x0008, 0x0060)],
        overwrite_database=True
    )

    print("Database length:", len(database))
    print("R01-005 patient :", database["R01-005"])
    print("R01-005 patient :", database[0])
