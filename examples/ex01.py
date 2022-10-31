"""
    @Title:             On-the-fly tasks.

    @Description:       Perform on-the-fly tasks on images.
"""

import env_examples  # Modifies path, DO NOT REMOVE

from dicom2hdf import PatientsDataGenerator
from dicom2hdf.transforms import Compose, ResampleD
import SimpleITK as sitk


if __name__ == "__main__":
    # ----------------------------------------------------------------------------------------------------------- #
    #                                    Perform on-thy-fly tasks on images                                       #
    # ----------------------------------------------------------------------------------------------------------- #
    patients_data_generator = PatientsDataGenerator(
        path_to_patients_folder="data/Patients",
        series_descriptions="data/series_descriptions.json",
        transforms=Compose(
            [
                ResampleD(keys=["CT", "Heart"], out_spacing=(1.5, 1.5, 1.5))
            ]
        )
    )

    for patient_data in patients_data_generator:
        print(f"Patient ID: {patient_data.patient_id}")

        for patient_image_data in patient_data.data:
            dicom_header = patient_image_data.image.dicom_header
            simple_itk_image = patient_image_data.image.simple_itk_image
            numpy_array_image = sitk.GetArrayFromImage(simple_itk_image)

            """Perform any tasks on images on-the-fly."""
            print(numpy_array_image.shape)
