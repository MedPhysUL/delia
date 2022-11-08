"""
    @Title:             Radiomics extraction.

    @Description:       Extract radiomics from CT and PET images with a given 'Heart' contour.
"""

import env_examples  # Modifies path, DO NOT REMOVE

from dicom2hdf import PatientsDataGenerator
from dicom2hdf.radiomics import RadiomicsDataset
from dicom2hdf.transforms import Compose, CopySegmentationsD, PETtoSUVD
from radiomics.featureextractor import RadiomicsFeatureExtractor


if __name__ == "__main__":
    # ----------------------------------------------------------------------------------------------------------- #
    #                                         Logs Setup (Optional)                                               #
    # ----------------------------------------------------------------------------------------------------------- #
    env_examples.configure_logging("logging_conf.yaml")

    # ----------------------------------------------------------------------------------------------------------- #
    #                                      Create patients data generator                                         #
    # ----------------------------------------------------------------------------------------------------------- #
    patients_data_generator = PatientsDataGenerator(
        path_to_patients_folder="data/patients",
        series_descriptions="data/radiomics_series_descriptions.json",
        transforms=Compose(
            [
                PETtoSUVD(keys=["TEP"]),
                CopySegmentationsD(segmented_image_key="CT_THORAX", unsegmented_image_key="TEP")
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
        patients_data_generator=patients_data_generator,
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
        patients_data_generator=patients_data_generator,
        organ="Heart",
        image_name="TEP"
    )
