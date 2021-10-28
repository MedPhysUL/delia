import enum
from typing import NamedTuple, Callable

from src.data_readers.segmentation.nrrd.label_map_volume import LabelMapVolume
from src.data_readers.segmentation.nrrd.segmentation_label_map_representation import SegmentationLabelMapRepresentation


class SegmentationCategory(NamedTuple):
    name: str
    file_extension: str
    loading_class: Callable


class SegmentationCategories(SegmentationCategory, enum.Enum):

    LABEL_MAP_VOLUME: SegmentationCategory = SegmentationCategory(
        name="label_map_volume",
        file_extension=".nrrd",
        loading_class=LabelMapVolume
    )

    SEGMENTATION_LABEL_MAP_REPRESENTATION: SegmentationCategory = SegmentationCategory(
        name="segmentation_label_map_representation",
        file_extension=".seg.nrrd",
        loading_class=SegmentationLabelMapRepresentation
    )
