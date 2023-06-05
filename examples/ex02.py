"""
    @Title:             Radiomics extraction.

    @Description:       Extract radiomics from CT and PET images with a given 'Heart' contour.
"""

import env_examples  # Modifies path, DO NOT REMOVE

from delia.extractors import PatientsDataExtractor
from delia.radiomics import RadiomicsDataset, RadiomicsFeatureExtractor
from delia.transforms import Compose, CopySegmentationsD, PETtoSUVD


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
        tag_values="data/radiomics_tag_values.json",
        transforms=Compose(
            [
                PETtoSUVD(keys=["PET"]),
                CopySegmentationsD(segmented_image_key="CT_THORAX", unsegmented_image_key="PET")
            ]
        )
    )

    # ----------------------------------------------------------------------------------------------------------- #
    #       Extract radiomics features of the CT image from the segmentation of the heart made on the CT image    #
    # ----------------------------------------------------------------------------------------------------------- #

    CT_radiomics_dataset = RadiomicsDataset(path_to_dataset="data/CT_radiomics")

    CT_radiomics_dataset.extractor = RadiomicsFeatureExtractor(
        path_to_params="features_extractor_params_CT.yaml",
        geometryTolerance=1e-4
    )

    CT_radiomics_dataset.create(
        patients_data_extractor=patients_data_extractor,
        organ="Heart",
        image_name="CT_THORAX"
    )

    # ----------------------------------------------------------------------------------------------------------- #
    #       Extract radiomics features of the PT image from the segmentation of the heart made on the CT image    #
    # ----------------------------------------------------------------------------------------------------------- #
    PT_radiomics_dataset = RadiomicsDataset(path_to_dataset="data/PT_radiomics")

    PT_radiomics_dataset.extractor = RadiomicsFeatureExtractor(
        path_to_params="features_extractor_params_PT.yaml",
        geometryTolerance=1e-4
    )

    PT_radiomics_dataset.create(
        patients_data_extractor=patients_data_extractor,
        organ="Heart",
        image_name="PET"
    )
