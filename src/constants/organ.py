import enum
from typing import List, NamedTuple


class Organ(NamedTuple):
    name: str
    segment_names: List[str]


class Organs(Organ, enum.Enum):

    PROSTATE: Organ = Organ(
        name="Prostate",
        segment_names=["Segment_1", "Prostate"]
    )

    RECTUM: Organ = Organ(
        name="Rectum",
        segment_names=["Segment_2", "Rectum"]
    )

    BLADDER: Organ = Organ(
        name="Bladder",
        segment_names=["Segment_3", "Bladder"]
    )
