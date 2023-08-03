"""
    @Title:             On-the-fly tasks.

    @Description:       Perform on-the-fly tasks on images.
"""

import env_examples  # Modifies path, DO NOT REMOVE

from delia.extractors import PatientsDataExtractor
from delia.transforms import Compose, CopySegmentationsD, MatchingCentroidSpatialCropD, PETtoSUVD, ResampleD
from monai.transforms import KeepLargestConnectedComponentD
import SimpleITK as sitk


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
        tag="SeriesDescription",
        tag_values="data/tag_values.json",
        transforms=Compose(
            [
                ResampleD(keys=["CT_THORAX", "Heart"], out_spacing=(1.5, 1.5, 1.5)),
                MatchingCentroidSpatialCropD(
                    segmentation_key="Heart",
                    matching_keys=["CT_THORAX"],
                    roi_size=(96, 96, 96)
                ),
                PETtoSUVD(keys=["PT"]),
                KeepLargestConnectedComponentD(keys=["Heart"]),
                CopySegmentationsD(segmented_image_key="CT_THORAX", unsegmented_image_key="PT")
            ]
        )
    )

    # ----------------------------------------------------------------------------------------------------------- #
    #                                    Perform on-thy-fly tasks on images                                       #
    # ----------------------------------------------------------------------------------------------------------- #
    for patient_data in patients_data_extractor:
        print(f"{'-'*20}\nPatient ID: {patient_data.patient_id}")

        for patient_image_data in patient_data.data:
            dicom_header = patient_image_data.image.dicom_header
            simple_itk_image = patient_image_data.image.simple_itk_image
            numpy_array_image = sitk.GetArrayFromImage(simple_itk_image)

            """Perform any tasks on images on-the-fly."""
            print("\nMODALITY:", dicom_header.Modality)
            print("IMAGE NAME:", patient_image_data.image.series_key)
            print("IMAGE SHAPE:", numpy_array_image.shape)
            print("IMAGE MEAN VALUE:", numpy_array_image.mean())

            segmentations = patient_image_data.segmentations
            if segmentations:
                for segmentation in segmentations:
                    for organ, sitk_label_map in segmentation.simple_itk_label_maps.items():
                        numpy_array_image = sitk.GetArrayFromImage(sitk_label_map)
                        print("ORGAN:", organ)
                        print("LABEL MAP SHAPE:", numpy_array_image.shape)
