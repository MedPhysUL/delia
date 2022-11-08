"""
    @Title:             On-the-fly tasks.

    @Description:       Perform on-the-fly tasks on images.
"""

import env_examples  # Modifies path, DO NOT REMOVE

from dicom2hdf.generators import PatientsDataGenerator
from dicom2hdf.transforms import Compose, CopySegmentationsD, PETtoSUVD, ResampleD
import SimpleITK as sitk


if __name__ == "__main__":
    # ----------------------------------------------------------------------------------------------------------- #
    #                                      Create patients data generator                                         #
    # ----------------------------------------------------------------------------------------------------------- #
    patients_data_generator = PatientsDataGenerator(
        path_to_patients_folder="data/patients",
        series_descriptions="data/series_descriptions.json",
        transforms=Compose(
            [
                ResampleD(keys=["CT_THORAX", "Heart"], out_spacing=(1.5, 1.5, 1.5)),
                PETtoSUVD(keys=["TEP"]),
                CopySegmentationsD(segmented_image_key="CT_THORAX", unsegmented_image_key="TEP")
            ]
        )
    )

    # ----------------------------------------------------------------------------------------------------------- #
    #                                    Perform on-thy-fly tasks on images                                       #
    # ----------------------------------------------------------------------------------------------------------- #
    for patient_data in patients_data_generator:
        print(f"Patient ID: {patient_data.patient_id}")

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
