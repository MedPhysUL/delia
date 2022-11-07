"""
    @file:              pet_to_suv.py
    @Author:            Maxence Larose

    @Creation Date:     10/2022
    @Last modification: 11/2022

    @Description:       This file contains the PETtoSUVd transform.
"""

from datetime import datetime
import logging
from typing import Dict, Hashable

import numpy as np
import pydicom
import SimpleITK as sitk

from dicom2hdf.transforms.physical_space.transform import PhysicalSpaceTransform, ImageData, KeysCollection, Mode

_logger = logging.getLogger(__name__)


class DefaultParams:
    WEIGHT = 75000  # [grams]
    SCAN_INJECTION_DELAY = 1.75 * 3600  # [seconds]
    HALF_LIFE = 6588  # [seconds]
    TOTAL_INJECTED_DOSE = 420_000_000  # [becquerels]


class PETtoSUVd(PhysicalSpaceTransform):
    """
    Transform a PET image to Standardized uptake value (SUV) in g/ml..
    """

    PET_MODALITY_NAME = "PT"

    def __init__(
            self,
            keys: KeysCollection
    ):
        """
        Initialize transform.

        Parameters
        ----------
        keys : KeysCollection
            Keys of the corresponding items to be transformed. Image keys are assumed to be arbitrary series keys
            defined in 'series_descriptions'. For the label maps, the keys are organ names. Note that if
            'series_descriptions' is None, the image keys are assumed to be modality names.
        """
        super().__init__(keys=keys)

    @staticmethod
    def get_patient_weight(header: pydicom.dataset.FileDataset) -> float:
        """
        Get patient weight or estimate it.

        Parameters
        ----------
        header : pydicom.dataset.FileDataset
            Dicom header.

        Returns
        -------
        weight : float
            Patient weight in grams.
        """
        if hasattr(header, "PatientWeight"):
            return float(header.PatientWeight) * 1000
        else:
            _logger.warning(f"Attribute 'PatientWeight' doesn't exist. Using estimated patient weight of "
                            f"{DefaultParams.WEIGHT / 1000} kg.")

            return DefaultParams.WEIGHT

    @staticmethod
    def get_time_delay_between_injection_and_scan(header: pydicom.dataset.FileDataset) -> float:
        """
        Get time delay between radiopharmaceutical injection and scan.

        Parameters
        ----------
        header : pydicom.dataset.FileDataset
            Dicom header.

        Returns
        -------
        time_delay : float
            Time delay in seconds.
        """
        if hasattr(header, "AcquisitionTime"):
            scan_time = datetime.strptime(header.AcquisitionTime, '%H%M%S.%f')

            if hasattr(header.RadiopharmaceuticalInformationSequence[0], "RadiopharmaceuticalStartTime"):
                injection_time = datetime.strptime(
                    header.RadiopharmaceuticalInformationSequence[0].RadiopharmaceuticalStartTime, '%H%M%S.%f'
                )

                return (scan_time - injection_time).seconds
            else:
                _logger.warning(f"Attribute 'RadiopharmaceuticalStartTime' doesn't exist. Using estimated time delay "
                                f"between injection and scan of {DefaultParams.SCAN_INJECTION_DELAY / 60} minutes, "
                                f"i.e. 90 min waiting time + 15 min preparation.")

                return DefaultParams.SCAN_INJECTION_DELAY
        else:
            _logger.warning(
                f"Attribute 'AcquisitionTime' doesn't exist. Using estimated time delay between injection and "
                f"scan of {DefaultParams.SCAN_INJECTION_DELAY / 60} minutes, i.e. 90 min waiting time + 15 min "
                f"preparation.")

            return DefaultParams.SCAN_INJECTION_DELAY

    @staticmethod
    def get_radionuclide_half_life(header: pydicom.dataset.FileDataset) -> float:
        """
        Get radionuclide half-life.

        Parameters
        ----------
        header : pydicom.dataset.FileDataset
            Dicom header.

        Returns
        -------
        half_life : float
            Half life in seconds.
        """
        if hasattr(header.RadiopharmaceuticalInformationSequence[0], "RadionuclideHalfLife"):
            return float(header.RadiopharmaceuticalInformationSequence[0].RadionuclideHalfLife)
        else:
            _logger.warning(
                f"Attribute 'RadionuclideHalfLife' doesn't exist. Using estimated radionuclide half-life of "
                f"{DefaultParams.HALF_LIFE} seconds.")

            return DefaultParams.HALF_LIFE

    @staticmethod
    def get_radionuclide_total_injected_dose(header: pydicom.dataset.FileDataset) -> float:
        """
        Get radionuclide total injected dose.

        Parameters
        ----------
        header : pydicom.dataset.FileDataset
            Dicom header.

        Returns
        -------
        injected_dose : float
            Injected dose in Bq.
        """
        if hasattr(header.RadiopharmaceuticalInformationSequence[0], "RadionuclideTotalDose"):
            return float(header.RadiopharmaceuticalInformationSequence[0].RadionuclideTotalDose)
        else:
            _logger.warning(f"Attribute 'RadionuclideTotalDose' doesn't exist. Using estimated total injected dose of "
                            f"{DefaultParams.TOTAL_INJECTED_DOSE / 1e6} MBq.")

            return DefaultParams.TOTAL_INJECTED_DOSE

    def compute_suv(self, sitk_pet_image: sitk.Image, dicom_header: pydicom.dataset.FileDataset) -> sitk.Image:
        """
        Computes Standardized uptake value (SUV) in g/ml.

        Parameters
        ----------
        sitk_pet_image : sitk.Image
            SimpleITK image of a PET scan where pixel intensities are related to FDG uptake.
        dicom_header : pydicom.dataset.FileDataset
            Dicom header.

        Returns
        -------
        sitk_suv_image : sitk.Image
            SimpleITK image of a PET scan where pixel intensities are SUV.
        """
        weight_grams = self.get_patient_weight(dicom_header)

        if hasattr(dicom_header, "RadiopharmaceuticalInformationSequence"):
            # Time delay between injection and acquisition
            time_delay = self.get_time_delay_between_injection_and_scan(header=dicom_header)

            # Half Life for Radionuclide # seconds
            half_life = self.get_radionuclide_half_life(header=dicom_header)

            # Total dose injected for Radionuclide
            injected_dose = self.get_radionuclide_total_injected_dose(header=dicom_header)

            # Calculate decay
            decay = np.exp(-np.log(2) * time_delay / half_life)

            # Calculate the dose decayed during procedure
            injected_dose_decay = injected_dose * decay  # [Bq]
        else:
            _logger.warning(
                f"Attribute 'RadiopharmaceuticalInformationSequence' doesn't exist. Using estimated time delay "
                f"between injection and scan of {DefaultParams.SCAN_INJECTION_DELAY / 60} minutes (90 min "
                f"waiting time, 15 min preparation), estimated radionuclide half-life of "
                f"{DefaultParams.HALF_LIFE} seconds and estimated total injected dose of "
                f"{DefaultParams.TOTAL_INJECTED_DOSE / 1e6} MBq.")

            decay = np.exp(-np.log(2) * DefaultParams.SCAN_INJECTION_DELAY / DefaultParams.HALF_LIFE)
            injected_dose_decay = DefaultParams.TOTAL_INJECTED_DOSE * decay

        # Calculate SUV [g/ml]
        suv = sitk_pet_image * weight_grams / injected_dose_decay

        return suv

    def __call__(self, data: Dict[str, ImageData]) -> Dict[Hashable, sitk.Image]:
        """
        Resample an itk_image to new out_spacing.

        Parameters
        ----------
        data : Dict[str, ImageData]
            A Python dictionary that contains ImageData.

        Returns
        -------
        transformed_image : Dict[Hashable, sitk.Image]
            A Python dictionary that contains transformed SimpleITK images.
        """
        d = dict(data)

        for key in self.key_iterator(d):
            if self._mode == Mode.NONE:
                raise AssertionError("Transform mode must be set before __call__.")
            elif not d[key].dicom_header:
                raise AssertionError(f"The 'PETtoSUV' can't be used on segmentations. The 'PETtoSUV' can only be used "
                                     f"on {self.PET_MODALITY_NAME} modality.")
            elif str(d[key].dicom_header.Modality) != self.PET_MODALITY_NAME:
                raise AssertionError(f"Tried using 'PETtoSUV' transform on {d[key].dicom_header.Modality} modality. "
                                     f"The 'PETtoSUV' can only be used on {self.PET_MODALITY_NAME} modality.")
            else:
                d[key] = self.compute_suv(sitk_pet_image=d[key].simple_itk_image, dicom_header=d[key].dicom_header)

        return d


PETtoSUVD = PETtoSUVDict = PETtoSUVd
