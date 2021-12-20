import json
from typing import NamedTuple

import h5py
import matplotlib.pyplot as plt
import numpy as np
import SimpleITK as sitk


class Modality(NamedTuple):
    CT = "CT"
    PT = "PT"


class Tags(NamedTuple):
    PIXEL_SPACING = "00280030"
    POSITION = "00200032"
    ORIENTATION = "00200037"


def resample_itk_image(
        original_image: np.ndarray,
        target_image: np.ndarray,
        original_dicom_header: dict,
        target_dicom_header: dict
):
    original_itk_image = sitk.GetImageFromArray(original_image)
    original_spacing = original_dicom_header[Tags.PIXEL_SPACING]["Value"] + [4.0]
    original_origin = original_dicom_header[Tags.POSITION]["Value"]

    original_itk_image.SetSpacing(original_spacing)
    original_itk_image.SetOrigin(original_origin)

    transposed_target_image = target_image.transpose(2, 0, 1)
    target_size = transposed_target_image.shape
    target_spacing = target_dicom_header[Tags.PIXEL_SPACING]["Value"] + [2.5]
    target_origin = target_dicom_header[Tags.POSITION]["Value"]

    resample = sitk.ResampleImageFilter()
    resample.SetOutputSpacing(target_spacing)
    resample.SetSize(target_size)
    resample.SetOutputOrigin(target_origin)
    resample.SetTransform(sitk.Transform())
    resample.SetInterpolator(sitk.sitkBSplineResamplerOrder2)

    resampled_image = resample.Execute(original_itk_image)
    resampled_image = sitk.GetArrayFromImage(resampled_image)

    return resampled_image


if __name__ == "__main__":
    path = "data/patient_dataset.h5"
    hf = h5py.File(name=path, mode="r")

    CT_pixel_values_in_all_patients_roi = []
    PT_pixel_values_in_all_patients_roi = []
    patient_number = 0
    for patient, group in hf.items():
        print("Patient name:", patient)
        CT_dicom_header, CT_image, PT_dicom_header, PT_image, prostate_mask = None, None, None, None, None

        try:
            for volume_idx, volume in group.items():
                volume_attributes = dict(volume.attrs)
                modality = volume_attributes["modality"]
                print("Modality:", modality)

                if modality == Modality.CT:
                    CT_dicom_header = json.loads(volume["dicom_header"][()])

                    prostate_segmentation = volume["Prostate_label_map"][:]
                    prostate_mask = np.where(prostate_segmentation)

                    CT_image = volume["image"][:]
                    CT_roi = CT_image[prostate_mask]
                    CT_pixel_values_in_all_patients_roi.extend(CT_roi)

                elif modality == Modality.PT:
                    PT_dicom_header = json.loads(volume["dicom_header"][()])

                    PT_image = volume["image"][:]

                    # print(np.mean(PT_image))


            PT_image = resample_itk_image(
                original_image=PT_image,
                target_image=CT_image,
                original_dicom_header=PT_dicom_header,
                target_dicom_header=CT_dicom_header
            )
            # print(np.mean(PT_image))

            PT_roi = PT_image[prostate_mask]

            PT_pixel_values_in_all_patients_roi.extend(PT_roi)

            patient_number += 1
        except:
            print(f"Patient: {patient} ignored")

        print("\n")

    print(f"Total of {patient_number} patients")
    print(f"{'-'*30}  CT  {'-'*30}")
    print("Maximum: ", np.max(CT_pixel_values_in_all_patients_roi))
    print("Minimum: ", np.min(CT_pixel_values_in_all_patients_roi))
    print("Mean: ", np.mean(CT_pixel_values_in_all_patients_roi))
    print("Median: ", np.median(CT_pixel_values_in_all_patients_roi))

    plt.hist(CT_pixel_values_in_all_patients_roi, bins=25)
    plt.show()

    bins = np.arange(-1025, 1275, 25)
    plt.hist(CT_pixel_values_in_all_patients_roi, bins=bins)
    plt.show()

    print(f"{'-'*30}  PT  {'-'*30}")
    print("Maximum: ", np.max(PT_pixel_values_in_all_patients_roi))
    print("Minimum: ", np.min(PT_pixel_values_in_all_patients_roi))
    print("Mean: ", np.mean(PT_pixel_values_in_all_patients_roi))
    print("Median: ", np.median(PT_pixel_values_in_all_patients_roi))
    print(f"Last 20 values out of {len(PT_pixel_values_in_all_patients_roi)}: ",
          np.sort(PT_pixel_values_in_all_patients_roi)[-20:]
          )

    plt.hist(PT_pixel_values_in_all_patients_roi, bins=25)
    plt.show()

    bins = np.arange(0, 650, 10)
    plt.hist(CT_pixel_values_in_all_patients_roi, bins=bins)
    plt.show()
