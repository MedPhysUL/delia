"""
    @Title:             Database creation + handling of patients who failed.

    @Description:       Create the (possibly partial) HDF5 database, update the tag values dictionary using the
                        information from the failed patients' images, and finally create the full HDF5 database.
"""

import env_examples  # Modifies path, DO NOT REMOVE

import json
from typing import Dict, List, Union

from delia.databases import PatientsDatabase
from delia.extractors import PatientsDataExtractor, PatientWhoFailed


def get_updated_tag_values(
        patients_who_failed: List[PatientWhoFailed],
        tag_values: Union[str, Dict[str, List[str]]]
) -> Union[str, Dict[str, List[str]]]:
    """
    Add a tag value to the tag value list of the given series key.

    Parameters
    ----------
    patients_who_failed : List[PatientWhoFailed]
        List of patients with one or more images not added to the HDF5 database due to the absence of the series in
        the patient record.
    tag_values : Union[str, Dict[str, List[str]]], default = None.
        A dictionary that contains the desired tag's values for the images that absolutely needs to be extracted
        from the patient's file. Keys are arbitrary names given to the images we want to add and values are lists of
        values associated with the specified tag. The images associated with these tag values do not need to have a
        corresponding segmentation. In fact, the whole point of adding a way to specify the values for a specified tag
        that must be added to the database is to be able to add images without their segmentation.
    """
    for patient in patients_who_failed:
        for image, image_tag_values in patient.failed_images.items():
            if not any([series in tag_values[image] for series in patient.available_tag_values]):
                while True:
                    new_tag_value = input(
                        f"\nNo available series for {image}. \nAvailable series are "
                        f"{patient.available_tag_values}. \nName of the tag value to add : ")

                    print(f"Given tag value name is {new_tag_value}.")

                    if new_tag_value in patient.available_tag_values:
                        print(f"tag value successfully added to the tag values json file.")
                        break
                    else:
                        print(f"Invalid tag value! \n{new_tag_value} not found in the patient's "
                              f"dicom files. Please try again.")

                tag_values[image] += [new_tag_value]

    return tag_values


if __name__ == "__main__":
    # ----------------------------------------------------------------------------------------------------------- #
    #     Create database (some images of some patients might fail to be added to the database due to the         #
    #                               absence of the tag value in the patient record)                               #
    # ----------------------------------------------------------------------------------------------------------- #
    patients_data_extractor = PatientsDataExtractor(
        path_to_patients_folder="data/patients",
        tag="SeriesDescription",
        tag_values="data/incorrect_tag_values.json"
    )

    database = PatientsDatabase(path_to_database="data/patients_database.h5")

    patients_who_failed = database.create(
        patients_data_extractor=patients_data_extractor,
        overwrite_database=True
    )

    # Print list of patients who failed
    print(f"Patients who failed the pipeline : {patients_who_failed}")

    # ----------------------------------------------------------------------------------------------------------- #
    #                                              Update tag values                                              #
    # ----------------------------------------------------------------------------------------------------------- #
    with open("data/incorrect_tag_values.json", "r") as json_file:
        tag_values = json.load(json_file)

    updated_tag_values = get_updated_tag_values(
        patients_who_failed=patients_who_failed,
        tag_values=tag_values
    )

    with open("data/incorrect_tag_values.json", 'w', encoding='utf-8') as json_file:
        json.dump(updated_tag_values, json_file, ensure_ascii=False, indent=4)

    # ----------------------------------------------------------------------------------------------------------- #
    #                                           Create complete database                                          #
    # ----------------------------------------------------------------------------------------------------------- #
    patients_data_extractor = PatientsDataExtractor(
        path_to_patients_folder="data/patients",
        tag_values=updated_tag_values
    )

    patients_who_failed = database.create(
        patients_data_extractor=patients_data_extractor,
        tags_to_use_as_attributes=[(0x0008, 0x103E), (0x0020, 0x000E), (0x0008, 0x0060)],
        overwrite_database=True
    )

    # Print list of patients who failed. This list should be empty now.
    print(f"Patients who failed the pipeline : {patients_who_failed}")
