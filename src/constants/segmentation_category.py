import enum
from typing import NamedTuple, Callable

from src.data_readers.segmentation.nrrd.label_map_volume_builder import LabelMapVolumeBuilder
from src.data_readers.segmentation.nrrd.segmentation_label_map_representation_builder import \
    SegmentationLabelMapRepresentationBuilder


class SegmentationCategory(NamedTuple):
    name: str
    file_extension: str
    builder: Callable


class SegmentationCategories(SegmentationCategory, enum.Enum):

    LABEL_MAP_VOLUME: SegmentationCategory = SegmentationCategory(
        name="label_map_volume",
        file_extension=".nrrd",
        builder=LabelMapVolumeBuilder
    )

    SEGMENTATION_LABEL_MAP_REPRESENTATION: SegmentationCategory = SegmentationCategory(
        name="segmentation_label_map_representation",
        file_extension=".seg.nrrd",
        builder=SegmentationLabelMapRepresentationBuilder
    )
