"""
    @file:              transform.py
    @Author:            Maxence Larose

    @Creation Date:     11/2022
    @Last modification: 11/2022

    @Description:       This file contains the DataTransform abstract class which is used to define transforms
                        that can be applied to images and segmentations.
"""

from abc import abstractmethod
from typing import Collection, Dict, Hashable, Union

from monai.transforms import MapTransform

from delia.utils.data_model import ImageAndSegmentationDataModel

KeysCollection = Union[Collection[Hashable], Hashable]


class DataTransform(MapTransform):
    """
    DataTransform abstract class.
    """

    def __init__(self, keys: KeysCollection) -> None:
        """
        Initialize transform keys.

        Parameters
        ----------
        keys : KeysCollection
            Keys of the corresponding items to be transformed. Image keys are assumed to be arbitrary series keys
            defined in 'tag_values'. For the label maps, the keys are organ names. Note that if
            'tag_values' is None, the image keys are assumed to be modality names.
        """
        super().__init__(keys=keys, allow_missing_keys=True)

    @abstractmethod
    def __call__(self, data: Dict[str, ImageAndSegmentationDataModel]) -> Dict[Hashable, ImageAndSegmentationDataModel]:
        """
        Apply the transformation.

        Parameters
        ----------
        data : Dict[str, ImageAndSegmentationDataModel]
            A Python dictionary that contains ImageAndSegmentationDataModel.

        Returns
        -------
        transformed_data : Dict[Hashable, ImageAndSegmentationDataModel]
            A Python dictionary that contains transformed ImageAndSegmentationDataModel.
        """
        raise NotImplementedError
