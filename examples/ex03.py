"""
    @Title:             Logging + database creation.

    @Description:       Configure logging and create database.
"""

import env_examples  # Modifies path, DO NOT REMOVE

from delia.databases import PatientsDatabase
from delia.extractors import PatientsDataExtractor
from delia.transforms import (
    PETtoSUVD,
    ResampleD
)
from monai.transforms import (
    CenterSpatialCropD,
    Compose,
    ScaleIntensityD,
    ThresholdIntensityD
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
                ResampleD(keys=["CT_THORAX", "TEP", "Heart"], out_spacing=(1.5, 1.5, 1.5)),
                CenterSpatialCropD(keys=["CT_THORAX", "TEP", "Heart"], roi_size=(1000, 160, 160)),
                ThresholdIntensityD(keys=["CT_THORAX"], threshold=-250, above=True, cval=-250),
                ThresholdIntensityD(keys=["CT_THORAX"], threshold=500, above=False, cval=500),
                ScaleIntensityD(keys=["CT_THORAX"], minv=0, maxv=1),
                PETtoSUVD(keys=["TEP"])
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

    print("R01-005 patient :", database["R01-005"])
