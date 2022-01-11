"""
    @file:              patient_data_reader.py
    @Author:            Maxence Larose

    @Creation Date:     10/2021
    @Last modification: 01/2022

    @Description:       This file contains the PatientDataReader class which is used to read dicom files AND
                        segmentation files.
"""

import logging
from typing import Dict, List, Optional

from src.data_model import PatientDataModel
from ..dicom.dicom_reader import DicomReader
from .patient_data_query_context import PatientDataQueryContext


class PatientDataReader(DicomReader):
    """
    A class used to read dicom files AND segmentation files.
    """

    def __init__(
            self,
            path_to_dicom_folder: str,
            verbose: bool,
            organs: Optional[Dict[str, List[str]]] = None,
            paths_to_segmentations: Optional[List[str]] = None,
            series_descriptions: Optional[Dict[str, List[str]]] = None,
    ):
        """
        Used to check availability of given series' uid and series descriptions in the patient's dicom files.

        Parameters
        ----------
        path_to_dicom_folder : str
            Path to the folder containing the patient dicom files.
        verbose : bool
            True to log/print some information else False.
        organs : Optional[Dict[str, List[str]], None], default = None.
            A dictionary that contains the organs and their associated segment names. Keys are arbitrary organ names
            and values are lists of possible segment names.
        paths_to_segmentations : Optional[List[str]], default = None.
            A list of paths to the segmentation files. The name of the segmentation files must include the series uid
            of their corresponding image, i.e. the image on which the segmentation was made.
        series_descriptions : Optional[Dict[str, List[str]]], default = None.
            A dictionary that contains the series descriptions of the images that absolutely needs to be extracted from
            the patient's file. Keys are arbitrary names given to the images we want to add and values are lists of
            series descriptions. The images associated with these series descriptions do not need to have a
            corresponding segmentation. In fact, the whole point of adding a way to specify the series descriptions that
            must be added to the dataset is to be able to add images without segmentation.
        """
        super(PatientDataReader, self).__init__(path_to_dicom_folder=path_to_dicom_folder)
        if paths_to_segmentations:
            if any(path for path in paths_to_segmentations) and organs is None:
                raise AssertionError("The variable organs is required. It is a dictionary where keys are arbitrary"
                                     " organ names and values are lists of possible segment names.")

        self._dicom_headers = self.get_dicom_headers(verbose=verbose)
        self._organs = organs
        self._paths_to_segmentations = paths_to_segmentations
        self._series_descriptions = series_descriptions
        self._verbose = verbose

        if paths_to_segmentations is not None:
            if verbose:
                logging.info("\nChecking availability of given series uids...")
            self.check_availability_of_given_series_uids()
            if verbose:
                logging.info("Done.\n")
        if series_descriptions is not None:
            if verbose:
                logging.info("Checking availability of given series description...")
            self.check_availability_of_given_series_description()
            if verbose:
                logging.info("Done.")

    @property
    def patient_name(self) -> str:
        """
        Patient name.

        Returns
        -------
        patient_name : str
            Patient name.
        """
        return str(self._dicom_headers[0].PatientName)

    @property
    def paths_to_segmentations(self) -> List[str]:
        """
        Paths to segmentations property.

        Returns
        -------
        paths_to_segmentations : List[str]
            A list of paths to the segmentation files. The name of the segmentation files must include the series uid
            of their corresponding image, i.e. the image on which the segmentation was made.
        """
        return self._paths_to_segmentations

    @property
    def series_descriptions(self) -> Dict[str, List[str]]:
        """
        Series descriptions setter.

        Returns
        -------
        series_descriptions : Dict[str, List[str]]
            A dictionary that contains the series descriptions of the images that absolutely needs to be extracted from
            the patient's file. Keys are arbitrary names given to the images we want to add and values are lists of
            series descriptions.
        """
        return self._series_descriptions

    @series_descriptions.setter
    def series_descriptions(self, series_descriptions: Dict[str, List[str]]):
        """
        Series descriptions setter.

        Parameters
        ----------
        series_descriptions : Dict[str, List[str]]
            A dictionary that contains the series descriptions of the images that absolutely needs to be extracted from
            the patient's file. Keys are arbitrary names given to the images we want to add and values are lists of
            series descriptions. The images associated with these series descriptions do not need to have a
            corresponding segmentation. In fact, the whole point of adding a way to specify the series descriptions that
            must be added to the dataset is to be able to add images without segmentation. the patient dataset.
        """
        items = list(series_descriptions.items())
        for previous_items, current_items in zip(items, items[1:]):
            set_intersection = set(previous_items[1]) & set(current_items[1])

            if bool(set_intersection):
                raise AssertionError(f"\nThe dictionary of series descriptions should not contain the same series names"
                                     f" for different images/modalities. \nHowever, here we find the series names "
                                     f"{previous_items[1]} for the {previous_items[0]} image and {current_items[1]} "
                                     f"for the {current_items[0]} image. \nClearly, the images series values are "
                                     f"overlapping because of the series named {set_intersection}.")

        self.series_descriptions = series_descriptions

    @property
    def available_series_descriptions(self) -> List[str]:
        """
        Available series descriptions.

        Returns
        -------
        available_series_descriptions : List[str]
            Available series descriptions in the patient dicom files.
        """
        available_series_descriptions = [
            dicom_header.SeriesDescription for dicom_header in self._dicom_headers
        ]

        return available_series_descriptions + ["None"]

    @property
    def available_series_uids(self) -> List[str]:
        """
        Available series' uids.

        Returns
        -------
        available_series_uids : List[str]
            Available series uids in the patient dicom files.
        """
        available_series_uid = [
            dicom_header.SeriesInstanceUID for dicom_header in self._dicom_headers
        ]

        return available_series_uid

    def update_series_descriptions(self, series_key: str) -> None:
        """
        Add a series description to the series description list of the given series key.

        Parameters
        ----------
        series_key : str
            Series key.
        """
        logging.info(f"\nNo available series for {series_key}. \nAvailable series are "
                     f"{self.available_series_descriptions}. \nPlease write in the following location the name of the "
                     f"series to add. If the image does not require any description, write None.")

        while True:
            new_series_description = input(f"Name of the series description to add (modality = {series_key}): ")

            if new_series_description in self.available_series_descriptions:
                logging.info("Series name successfully added to the series descriptions json file.\n")
                break
            else:
                logging.info(f"The given series description name is {new_series_description}. \nHowever, this is NOT "
                             f"one of the available series description found in the patient's dicom files. \nAvailable "
                             f"series are {self.available_series_descriptions}. \nPlease try again.")

        self.series_descriptions[series_key] += [new_series_description]

    def check_availability_of_given_series_description(self) -> None:
        """
        Check availability of given series description in the patient's dicom files.
        """
        for series_key, series_description_list in self.series_descriptions.items():
            if any(series in self.available_series_descriptions for series in series_description_list):
                pass
            else:
                self.update_series_descriptions(series_key)
                self.check_availability_of_given_series_description()

    def check_availability_of_given_series_uids(self) -> None:
        """
        Check availability of given series uids in the patient's dicom files.
        """
        for path_to_segmentation in self.paths_to_segmentations:
            if any(uid in path_to_segmentation for uid in self.available_series_uids):
                pass
            else:
                logging.warning(f"The given segmentation file name is {path_to_segmentation}. \nHowever, this file name"
                                f" does NOT contain any of the available series uids found in the patient's dicom "
                                f"files. \nAvailable series uids are {self.available_series_uids}.")

    def get_patient_dataset(self) -> PatientDataModel:
        """
        Get the patient dataset.

        Returns
        -------
        patient_dataset : PatientDataModel
            A named tuple grouping the patient's data extracted from its dicom files and the patient's medical image
            segmentation data extracted from the segmentation files.
        """
        patient_data_context = PatientDataQueryContext(
            images_data=self.get_images_data(self._verbose),
            organs=self._organs,
            paths_to_segmentations=self._paths_to_segmentations,
            series_descriptions=self._series_descriptions
        )
        patient_dataset = patient_data_context.create_patient_data()

        if self._verbose:
            logging.debug("\nThe chosen patient data query strategy is called "
                          "'{patient_data_context.patient_data_query_strategy.name}'.")
            logging.info(f"\nA total of {len(patient_dataset.data)} images were added to the patient dataset, namely:")

            for image_and_segmentation_data in patient_dataset.data:
                modality = image_and_segmentation_data.image.dicom_header.Modality
                series_description = image_and_segmentation_data.image.dicom_header.SeriesDescription
                segmentation = image_and_segmentation_data.segmentation
                image_segmentation_available = True if segmentation else False
                segmented_organs = list(segmentation.binary_label_maps.keys()) if segmentation else None

                logging.info(f"---> Series Description ({series_description})"
                             f"\n     ---> Modality : {modality}"
                             f"\n     ---> Image Segmentation available: {image_segmentation_available}")

                if image_segmentation_available:
                    logging.info(f"     ---> Segmented organs : {segmented_organs}")

        return patient_dataset
