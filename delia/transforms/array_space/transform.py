"""
    @file:              transform.py
    @Author:            Maxence Larose

    @Creation Date:     03/2023
    @Last modification: 03/2023

    @Description:       This file contains the ArraySpaceTransform abstract class which is used to define transforms
                        that can be applied to images and segmentations.
"""

from abc import abstractmethod
from typing import Collection, Dict, Hashable, Union

import numpy as np
from monai.transforms import MapTransform

from ..tools import Mode

KeysCollection = Union[Collection[Hashable], Hashable]


class ArraySpaceTransform(MapTransform):
    """
    ArraySpaceTransform abstract class.
    """

    def __init__(self, keys: KeysCollection) -> None:
        """
        Initialize transform keys.

        Parameters
        ----------
        keys : KeysCollection
            Keys of the corresponding items to be transformed. Image keys are assumed to be arbitrary series keys
            defined in 'series_descriptions'. For the label maps, the keys are organ names. Note that if
            'series_descriptions' is None, the image keys are assumed to be modality names.
        """
        super().__init__(keys=keys, allow_missing_keys=True)
        self._mode = Mode.NONE

    @property
    def mode(self) -> Mode:
        """
        The transform mode, i.e. whether the single arrays on which to apply the transformation are images OR
        segmentations.

        Returns
        -------
        mode : Mode
            Transform mode.
        """
        return self._mode

    @mode.setter
    def mode(self, mode: Mode):
        """
        The transform mode, i.e. whether the single arrays on which to apply the transformation are images OR
        segmentations.

        Parameters
        ----------
        mode : Mode
            The transform mode, i.e. whether the single arrays on which to apply the transformation are images OR
            segmentations.
        """
        self._mode = mode

    @abstractmethod
    def __call__(self, data: Dict[Hashable, np.ndarray]) -> Dict[str, np.ndarray]:
        """
        Apply the transformation.

        Parameters
        ----------
        data : Dict[Hashable, np.ndarray]
            A Python dictionary that contains numpy array.

        Returns
        -------
        transformed_data : Dict[str, np.ndarray]
            A Python dictionary that contains transformed images.
        """
        raise NotImplementedError
