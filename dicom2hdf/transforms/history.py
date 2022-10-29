"""
    @file:              history.py
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
        self.history = []

        if transforms:
            self.append(transforms)

    def append(self, transforms: Union[Compose, MapTransform]) -> None:
        if isinstance(transforms, MapTransform):
            self.history.append(transforms.__dict__)
        elif isinstance(transforms, Compose):
            for transform in transforms.__dict__["transforms"]:
                self.history.append(dict({"name": transform.__class__.__name__}, **transform.__dict__))
        else:
            raise AssertionError("'transforms' must be Union[Compose, MapTransform].")
