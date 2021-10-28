import os
import enum
from typing import Union


class ExtendedEnum(enum.Enum):

    @classmethod
    def list(cls):
        return list(map(lambda c: c.value, cls))


def check_validity_of_given_path(
        path: str
) -> None:
    """
    Raise a ValueError if the given path doesn't exist.

    Parameters
    ----------
    path : str
        A path.

    Returns
    -------
    None
    """
    if not os.path.exists(path):
        raise FileNotFoundError(f"Given path {path} does not exist.")


def check_validity_of_given_name(name: str, enum_class: Union[enum.Enum, enum.IntEnum]) -> None:
    """
    Raise a ValueError if the given anatomical plane is not a member of the AnatomicalPlane Enum Class.

    Parameters
    ----------
    name : str
        Name.
    enum_class : Union[enum.Enum, enum.IntEnum]
        Class inheriting from enum.Enum or enum.IntEnum.

    Returns
    -------
    None
    """
    if name in enum_class.__members__:
        pass
    else:
        raise ValueError(f"Given member {name} is not allowed. Allowed members of {enum_class} are "
                         f"{list(enum_class.__members__)}.")
