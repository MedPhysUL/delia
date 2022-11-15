"""
    @file:              transforms_history.py
    @Author:            Maxence Larose

    @Creation Date:     10/2022
    @Last modification: 10/2022

    @Description:       This file contains the TransformsHistory class which is used to define a simple transforms
                        history container.
"""


from typing import Optional, Union

from monai.transforms import Compose, MapTransform


class TransformsHistory:
    """
    A simple history of the transforms applied on an image.
    """

    def __init__(self, transforms: Optional[Union[Compose, MapTransform]] = None):
        """
        Initialize history.

        Parameters
        ----------
        transforms : Optional[Union[Compose, MapTransform]]
            Transforms.
        """
        self.history = []

        if transforms:
            self.append(transforms)

    def append(self, transforms: Union[Compose, MapTransform]) -> None:
        """
        Append transforms to history.

        Parameters
        ----------
        transforms : Optional[Union[Compose, MapTransform]]
            Transforms.
        """
        if isinstance(transforms, MapTransform):
            self.history.append(transforms.__dict__)
        elif isinstance(transforms, Compose):
            for transform in transforms.__dict__["transforms"]:
                self.history.append(dict({"name": transform.__class__.__name__}, **vars(transform)))
        else:
            raise AssertionError("'transforms' must be Union[Compose, MapTransform].")

    @staticmethod
    def serialize(transforms: Union[Compose, MapTransform]) -> Union[dict, str]:
        """
        Serialize given transforms.

        Parameters
        ----------
        transforms : Optional[Union[Compose, MapTransform]]
            Transforms.

        Returns
        -------
        serialized_transforms : Union[dict, str]
            Serialized transforms.
        """
        try:
            return vars(transforms)
        except (AttributeError, TypeError):
            return "<not serializable>"
