"""
    @file:              copy_segmentations.py
    @Author:            Maxence Larose

    @Creation Date:     11/2022
    @Last modification: 11/2022

    @Description:       This file contains the CopySegmentationsd transform.
"""

from typing import Dict, Hashable

import SimpleITK as sitk

from dicom2hdf.data_model import ImageAndSegmentationDataModel, SegmentationDataModel
from dicom2hdf.transforms.data.transform import DataTransform


class CopySegmentationsd(DataTransform):
    """
    Copies all segmentations associated with an image and assigns the copies to another image. We also make sure to
    resample the label maps to the same size as the "new" image. For example, this makes it possible to associate
    the segmentations made on a CT image to a PET image that has been acquired during the same scan.
    """

    def __init__(
            self,
            segmented_image_key: str,
            unsegmented_image_key: str,
    ):
        """
        Initialize transform.

        Parameters
        ----------
        segmented_image_key : str
            Key of the segmented image from which to copy the segmentations. Image keys are assumed to be arbitrary
            series keys defined in 'series_descriptions'. Note that if 'series_descriptions' is None, the image keys
            are assumed to be modality names.
        unsegmented_image_key : str
            Key of the unsegmented image on which to copy the segmentations. Image keys are assumed to be arbitrary
            series keys defined in 'series_descriptions'. Note that if 'series_descriptions' is None, the image keys
            are assumed to be modality names.
        """
        super().__init__(keys=[segmented_image_key, unsegmented_image_key])

        self._segmented_image_key = segmented_image_key
        self._unsegmented_image_key = unsegmented_image_key

    def __call__(self, data: Dict[str, ImageAndSegmentationDataModel]) -> Dict[Hashable, ImageAndSegmentationDataModel]:
        """
        Copies all segmentations associated with an image and assigns the copies to another image.

        Parameters
        ----------
        data : Dict[str, ImageAndSegmentationDataModel]
            A Python dictionary that contains ImageAndSegmentationDataModel.

        Returns
        -------
        transformed_data : Dict[Hashable, ImageAndSegmentationDataModel]
            A Python dictionary that contains transformed ImageAndSegmentationDataModel.
        """
        d = dict(data)

        image, segmentations = None, None
        for key in self.key_iterator(d):
            if key == self._segmented_image_key:
                segmentations = d[key].segmentations
            if key == self._unsegmented_image_key:
                image = d[key].image

                if d[key].segmentations:
                    raise AssertionError(f"'CopySegmentationsd' found segmentations associated to 'unsegmented_image' "
                                         f"= {self._segmented_image_key}. Unsegmented images are supposed to be "
                                         f"unsegmented.")

        if not image:
            raise AssertionError(f"'CopySegmentationsd' found no image associated to 'unsegmented_image' = "
                                 f"{self._unsegmented_image_key}.")
        if not segmentations:
            raise AssertionError(f"'CopySegmentationsd' found no segmentations associated to 'segmented_image' = "
                                 f"{self._segmented_image_key}.")

        new_segmentations = []
        for segmentation in segmentations:
            new_label_maps = {}
            for organ, mask in segmentation.simple_itk_label_maps.items():
                resampled_mask = sitk.Resample(
                    mask,
                    image.simple_itk_image,
                    sitk.Transform(),
                    sitk.sitkNearestNeighbor,
                    0,
                    mask.GetPixelID()
                )

                new_label_maps[organ] = resampled_mask

            new_segmentations.append(
                SegmentationDataModel(modality=segmentation.modality, simple_itk_label_maps=new_label_maps)
            )

        d[self._unsegmented_image_key].segmentations = new_segmentations

        return d


CopySegmentationsD = CopySegmentationsDict = CopySegmentationsd
