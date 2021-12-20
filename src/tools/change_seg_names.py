from src.data_readers.patient_data_generator import PatientDataGenerator
from root import *
from typing import NamedTuple, Optional, List
import os


class PathsToPatientFolderAndSegmentations(NamedTuple):
    """
    Namedtuple of paths to patient folder and segmentations.
    """
    path_to_patient_folder: Optional[str] = None
    path_to_segmentations: Optional[List[str]] = None


paths_to_patients_folder_and_segmentations = []

for path in os.listdir(PathName.PATH_TO_PATIENTS_FOLDER):
    absolute_path = os.path.join(PathName.PATH_TO_PATIENTS_FOLDER, path, "IMAGES")
    path_tuple = PathsToPatientFolderAndSegmentations(
        path_to_patient_folder=absolute_path
    )

    paths_to_patients_folder_and_segmentations.append(path_tuple)


patient_data_generator = PatientDataGenerator(
    paths_to_patients_folder_and_segmentations=paths_to_patients_folder_and_segmentations,
    path_to_series_description_json=os.path.join(PathName.PATH_TO_DATA_FOLDER, "series_descriptions.json")
)

for i, patient_dataset in enumerate(patient_data_generator):
    print(f"{'-'*90}")
    print(paths_to_patients_folder_and_segmentations[i].path_to_patient_folder)
    print(patient_dataset.patient_name)

    print(patient_dataset.data[0].image.dicom_header.Modality)
    print(patient_dataset.data[0].image.dicom_header.SeriesInstanceUID)

    print(patient_dataset.data[1].image.dicom_header.Modality)
    print(patient_dataset.data[1].image.dicom_header.SeriesInstanceUID)

    print("\n")

